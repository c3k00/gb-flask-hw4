import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from aiohttp import ClientSession, ClientConnectorError
import asyncio
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image_urls = request.form.getlist('image_urls')
        start_time = time.time()

        with ThreadPoolExecutor() as executor:
            thread_results = [executor.submit(download_image, url) for url in image_urls]
            for result in thread_results:
                result.result()

        with ProcessPoolExecutor() as executor:
            process_results = [executor.submit(download_image, url) for url in image_urls]
            for result in process_results:
                result.result()

        asyncio.run(download_images_async(image_urls))

        end_time = time.time()
        total_time = end_time - start_time
        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
        return render_template('index.html', total_time=total_time, uploaded_files=uploaded_files)

    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', uploaded_files=uploaded_files)

@app.route('/uploads', methods=['POST'])
def uploads():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('index'))

def download_image(url):
    filename = os.path.basename(url)
    start_time = time.time()
    response = requests.get(url)
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
        f.write(response.content)
    end_time = time.time()
    print(f'Downloaded {filename} in {end_time - start_time:.2f} seconds')

async def download_images_async(image_urls):
    async with ClientSession() as session:
        tasks = []
        for url in image_urls:
            tasks.append(asyncio.create_task(download_image_async(session, url)))
        await asyncio.gather(*tasks)

async def download_image_async(session, url):
    filename = os.path.basename(url)
    start_time = time.time()
    try:
        async with session.get(url) as response:
            content = await response.read()
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
                f.write(content)
    except ClientConnectorError:
        print(f'Error downloading {filename}')
    end_time = time.time()
    print(f'Downloaded {filename} in {end_time - start_time:.2f} seconds')

if __name__ == '__main__':
    app.run(debug=True)