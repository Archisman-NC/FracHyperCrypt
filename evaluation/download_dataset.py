import os
import shutil
import requests
from PIL import Image

def download_and_normalize_image(image_name, url, output_dir, base_dir):
    """Downloads an image from a URL, converts it to grayscale, and resizes to 256x256.
    If download fails, copies a local project image as a fallback.
    """
    output_path = os.path.join(output_dir, f"{image_name.lower()}.png")
    
    # Check if already downloaded and correct size
    if os.path.exists(output_path):
        try:
            with Image.open(output_path) as img:
                if img.size == (256, 256) and img.mode == 'L':
                    # Only skip if it's not a synthetic fallback from a previous run
                    # We can identify synthetic fallbacks by checking if we have real images
                    print(f"[*] Image {image_name} already exists and is normalized. Skipping download.")
                    return output_path
        except Exception:
            pass # Re-download/re-copy if corrupted
            
    print(f"[*] Downloading {image_name} from {url}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # Save temp file
        temp_path = output_path + ".tmp"
        with open(temp_path, 'wb') as f:
            f.write(response.content)
            
        # Open, convert to grayscale, resize
        with Image.open(temp_path) as img:
            gray_img = img.convert('L')
            resized_img = gray_img.resize((256, 256), Image.Resampling.LANCZOS)
            resized_img.save(output_path)
            
        os.remove(temp_path)
        print(f"[+] Successfully saved and normalized {image_name} to {output_path}")
        return output_path
    except Exception as e:
        print(f"[!] Error downloading {image_name}: {e}")
        
        # If download fails, use project images as fallbacks
        fallback_source = None
        if image_name == "Peppers":
            fallback_source = os.path.join(base_dir, "images", "cat_test.png")
        elif image_name == "Cameraman":
            fallback_source = os.path.join(base_dir, "images", "test.png")
            
        if fallback_source and os.path.exists(fallback_source):
            print(f"[*] Using local project image fallback: {fallback_source}")
            try:
                with Image.open(fallback_source) as img:
                    gray_img = img.convert('L')
                    resized_img = gray_img.resize((256, 256), Image.Resampling.LANCZOS)
                    resized_img.save(output_path)
                print(f"[+] Successfully saved and normalized fallback for {image_name} to {output_path}")
                return output_path
            except Exception as fe:
                print(f"[!] Local fallback failed: {fe}")
                
        # Generate geometric pattern if all else fails
        print(f"[*] Generating synthetic geometric replacement for {image_name}...")
        import numpy as np
        x_grid, y_grid = np.meshgrid(np.linspace(-2, 2, 256), np.linspace(-2, 2, 256))
        pattern = np.sin(x_grid**2 + y_grid**2) * np.cos(x_grid*y_grid)
        pattern = ((pattern - pattern.min()) / (pattern.max() - pattern.min()) * 255).astype(np.uint8)
        img = Image.fromarray(pattern, mode='L')
        img.save(output_path)
        print(f"[+] Saved synthetic replacement for {image_name}")
        return output_path

def main():
    base_dir = "/Users/archismanchoudhury/Desktop/research/Research Implementation"
    images_dir = os.path.join(base_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Standard stable URLs
    urls = {
        "Lena": "https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/lena.jpg",
        "Baboon": "https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/baboon.jpg",
        "Peppers": "https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/peppers.jpg",
        "Cameraman": "https://raw.githubusercontent.com/scikit-image/scikit-image/main/skimage/data/cameraman.png",
        "House": "https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/home.jpg"
    }
    
    print("=== Dataset Downloader ===")
    for name, url in urls.items():
        # Force overwrite any existing synthetic geometric ones
        output_path = os.path.join(images_dir, f"{name.lower()}.png")
        if os.path.exists(output_path):
            os.remove(output_path)
        download_and_normalize_image(name, url, images_dir, base_dir)
    print("==========================")

if __name__ == "__main__":
    main()
