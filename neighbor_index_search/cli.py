
import argparse
import os
from .indexer import NeighborIndex
import PyPDF2
import cv2
import pytesseract
from pdf2image import convert_from_bytes
from docx import Document
import subprocess
import ollama
from pprint import pprint


def list_lib_docs(dir_path: str, print_files: bool = True):
    lib_docs_dir = os.path.abspath(dir_path)
    try:
        if not os.path.exists(lib_docs_dir):
            if print_files:
                print(f"Directory '{lib_docs_dir}' does not exist.")
            return []
        files = os.listdir(lib_docs_dir)
        if not files:
            if print_files:
                print(f"No files found in {dir_path}.")
        else:
            files = [f for f in files if os.path.isfile(os.path.join(lib_docs_dir, f))]
            return files
    except Exception as e:
        if print_files:
            print(f"Error listing files in {dir_path}: {e}")
        return []

def text_extractor(dir_path: str, file: str) -> str:
    text = ""
    with open(os.path.join(dir_path, file), 'rb') as f:
        file_body = f.read()

    if file.lower().endswith(".docx") or file.lower().endswith(".doc"):
        try:
            document = Document(os.path.join(dir_path, file))
            for paragraph in document.paragraphs:
                text += paragraph.text + ' '
        except Exception as e:
            print(f"Error reading {file}: {e}")

    elif file.lower().endswith(".pdf"):
        try:
            temporary_text = ""
            reader = PyPDF2.PdfReader(os.path.join(dir_path, file))
            for page_num in range(len(reader.pages)):
                temporary_text += reader.pages[page_num].extract_text() + ' '
            if any(c.isalpha() or c.isdigit() for c in temporary_text):
                text += temporary_text
            else:
                parent_folder = os.path.dirname(os.path.abspath(__file__))
                store_folder = os.path.join(parent_folder, "tmp")
                os.makedirs(store_folder, exist_ok=True)
                images = convert_from_bytes(file_body)
                for idx, img in enumerate(images):
                    img.save(os.path.join(store_folder, f'page{idx}.jpg'), 'JPEG')
                img_list = os.listdir(store_folder)
                img_list.sort()
                for i in range(len(img_list)):
                    img = cv2.imread(f"{store_folder}/{img_list[i]}")
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
                    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
                    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
                    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    im2 = img.copy()
                    for cnt in contours:
                        x, y, w, h = cv2.boundingRect(cnt)
                        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cropped = im2[y:y + h, x:x + w]
                        text += pytesseract.image_to_string(cropped)
                try:
                    for i in img_list:  subprocess.run(["rm", f"{store_folder}/{i}"])
                except: ...
        except Exception as e:
            print(f"Error reading PDF file {file}: {e}")
            print(f"Could not read PDF file {file}.")
    else:
        print(f"Unsupported file type: {file}. Only .doc .docx and .pdf are supported.")
    return text

def split_text_into_chunks(text: str, chunk_size=512, overlap=50):
    if not text:
        return []
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap if overlap < chunk_size else chunk_size
    return chunks

def main():
    parser = argparse.ArgumentParser(description="Neighbor Index Search CLI")
    parser.add_argument('--add', nargs=2, metavar=('ID', 'TEXT'), help='Add a collection with ID and TEXT')
    parser.add_argument('--search', metavar='QUERY', help='Search for QUERY and return hit with context')
    parser.add_argument('--add-doc', metavar='FILE', help='Add a document file (.pdf/.docx/.doc) to the index')
    parser.add_argument('--add-dir', metavar='DIR', help='Add all supported documents in a directory to the index')
    parser.add_argument('--list-models', action='store_true', help='List available embedding models from Ollama')
    args = parser.parse_args()

    if args.list_models:
        print("Available Ollama models:")
        pprint([_.model for _ in ollama.list().models])
        return

    index = NeighborIndex()

    if args.add:
        collection_id, text = args.add
        index.add_collection(collection_id, text)
        pprint({"Added collection": collection_id})

    elif args.add_doc:
        file_path = os.path.abspath(args.add_doc)
        dir_path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        text = text_extractor(dir_path, file_name)
        chunks = split_text_into_chunks(text)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_name}_chunk_{i}"
            index.add_collection(chunk_id, chunk)
            pprint({"Added chunk": chunk_id})
            
    elif args.add_dir:
        dir_path = os.path.abspath(args.add_dir)
        files = list_lib_docs(dir_path)
        if files:
            for file_name in files:
                text = text_extractor(dir_path, file_name)
                chunks = split_text_into_chunks(text)
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{file_name}_chunk_{i}"
                    index.add_collection(chunk_id, chunk)
                    pprint({"Added chunk": chunk_id})
        else:
            pprint({"No supported files found in": dir_path})
    elif args.search:
        results = index.search(args.search)
        for result in results:
            print("Search Hit:")
            pprint(result['hit'])
            print("Context:")
            pprint(result['context'])
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
