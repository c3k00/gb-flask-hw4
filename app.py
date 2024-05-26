import os
import time
import requests
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import argparse

def download_image(url):
    start_time = time.time()
    try:
        response = requests.get(url)
        response.raise_for_status()
        filename = os.path.basename(url)
        with open(filename, 'wb') as f:
            f.write(response.content)
        end_time = time.time()
        return filename, end_time - start_time
    except Exception as e:
        end_time = time.time()
        return str(e), end_time - start_time

async def async_download_image(url):
    start_time = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                filename = os.path.basename(url)
                content = await response.read()
                with open(filename, 'wb') as f:
                    f.write(content)
                end_time = time.time()
                return filename, end_time - start_time
    except Exception as e:
        end_time = time.time()
        return str(e), end_time - start_time

def threading_download(urls):
    start_time = time.time()
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_image, url) for url in urls]
        results = [future.result() for future in futures]
    total_time = time.time() - start_time
    return results, total_time

def multiprocessing_download(urls):
    start_time = time.time()
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(download_image, url) for url in urls]
        results = [future.result() for future in futures]
    total_time = time.time() - start_time
    return results, total_time

async def asyncio_download(urls):
    start_time = time.time()
    tasks = [async_download_image(url) for url in urls]
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    return results, total_time

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download images from URLs.')
    parser.add_argument('urls', nargs='+', help='List of image URLs to download')
    parser.add_argument('--method', choices=['threading', 'multiprocessing', 'asyncio'], default='threading', help='Download method to use')
    args = parser.parse_args()

    download_methods = {
        'threading': threading_download,
        'multiprocessing': multiprocessing_download,
        'asyncio': asyncio_download
    }

    if args.method == 'asyncio':
        loop = asyncio.get_event_loop()
        results, total_time = loop.run_until_complete(download_methods[args.method](args.urls))
    else:
        results, total_time = download_methods[args.method](args.urls)

    for filename, download_time in results:
        print(f"Downloaded {filename} in {download_time:.2f} seconds")

    print(f"Total time: {total_time:.2f} seconds")
    
    # python app.py https://example.com/image1.jpg https://example.com/image2.jpg --method threading
    
    # Замените threading на multiprocessing или asyncio для использования других методов скачивания.