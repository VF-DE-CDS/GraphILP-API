import requests
import tqdm
import zipfile

def download_example(url, target_directory, unzip=False):
    """ Download an example from the web
    
    :param url: URL to download from
    :param target_directory: directory to download into
    :param unzip: unzip data if zipped
    """
    
    target_name = target_directory + url.split("/")[-1]
    
    response = requests.get(url, stream=True)
    
    # get total size 
    total_size = int(response.headers.get('content-length', 0))
    
    # download file and show progress
    with open(target_name, 'wb') as output_file, tqdm.tqdm(
            desc  = target_name,
            total = total_size,
            unit  = 'iB',
            unit_scale = True,
            unit_divisor = 1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = output_file.write(data)
            progress_bar.update(size)
            
    with zipfile.ZipFile(target_name, 'r') as zip_reference:
        zip_reference.extractall(target_directory)
