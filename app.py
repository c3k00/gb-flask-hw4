import os
import time
import requests
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import argparse

def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        filename = os.path.basename(url)
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename, time.time()
    except Exception as e:
        return str(e), time.time()

async def async_download_image(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                filename = os.path.basename(url)
                content = await response.read()
                with open(filename, 'wb') as f:
                    f.write(content)
                return filename, time.time()
    except Exception as e:
        return str(e), time.time()

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
        print(f"Downloaded {filename} at {download_time}")

    print(f"Total time: {total_time}")
    
    # python app.py https://example.com/image1.jpg https://example.com/image2.jpg --method threading
    
    # Замените threading на multiprocessing или asyncio для использования других методов скачивания.