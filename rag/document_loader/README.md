# Overview
Document Loaders are the techniques that are used to load data from various sources like PDFs, text files, Web Pages, databases, CSV, JSON, Unstructured data, Research papers, and so on. 
After loading any type of data, They convert the data into a format that Large Language models can process. When the documents are loaded successfully, they are broken down into smaller parts or chunks and enable further processing by the language models.

There are different types of data loading techniques with LangChain such as Text Loader, PDF Loader, Directory Data Loader, CSV data Loading, YouTube transcript Loading, Scraping data from URLs in different ways, Research paper data loading, and Loading any custom data type.

## Text Loader
You can load any Text, or Markdown files with TextLoader. First, load the file and then look into the documents, the number of documents, page content, and metadata for each document.

```bash
from langchain_community.document_loaders import TextLoader

file_path = "/README.md"
loader = TextLoader(file_path)
# loader = TextLoader("data/sample.txt")

document = loader.load()

print(f"The whole documents are: \n{documents}\n")
print(f"\nThe number of documents : {len(documents)}\n")
print(f"Content of first document : \n{document[0].page_content}\n")
print(f"Metadata of first document : \n{document[0].metadata}")
```

## PDF Loader
To load PDF files, import the **pypdf** library. Then Load the PDF file and see the first document of all documents. Then you can see all the *page_content* & *metadata* for all the documents. From PDF, you will notice that the documents are based on the pages of the file.

```bash
# %pip install --upgrade --quiet pypdf
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("data/python book.pdf")
docs = loader.load()
print(docs[0])
print("\n\n")

# page_content & metadata for all documents
for doc in docs:
    print(doc.page_content)
    print(doc.metadata)
```

```
Lazy Loading creates generator objects at the time of loading files. It refers to a technique where data are loaded only when they are actually needed. 
It is useful when you are dealing with large datasets or files where loading everything at a time will be problematic or resource-intensive.
So, it helps to load documents when it is required which saves both memory and processing time.
```
```bash
loader = PyPDFLoader("data/python book.pdf")
lazy_doc = loader.lazy_load()
print(lazy_doc)

for doc in lazy_doc:
    print(doc.metadata)
    print("-----------Content----------")
    print(doc.page_content)
    break
```

## Directory Data Loader
You can load multiple files from a directory with the Directory Loader function. You can provide extra keyword arguments like show progress, silent errors, loader_cls, etc. **Show progress** will show how many files have been loaded. **Silent errors** are used to skip the files that can not be loaded and continue the load process. **loader_cls** is used to specify the data loader function. You may use other loaders like python-loader, pdf loader, XML loader, or others based on the data type. By default, Directoryloader uses the UnstructuredLoader class.

```bash
from langchain_community.document_loaders import DirectoryLoader
loader = DirectoryLoader("data/", glob="**/*.md", show_progress=True, silent_errors=True,loader_cls=TextLoader)
docs = loader.load()
print(docs)
```

## CSV Loader
Let’s load the CSV with the CSV Loader class. Also, you can define the csv_args to get the exact data.

```bash
from langchain_community.document_loaders import CSVLoader
file_path = "data/train_and_test2.csv"
loader = CSVLoader(file_path=file_path)
# loader = CSVLoader(
#     file_path=file_path,
#     csv_args={
#         "delimiter": ",",
#         "quotechar": '"',
#         "fieldnames": ["Id", "email", "class"],
#     },
# )

docs = loader.load()
print(docs)
```

## YouTube Transcript Loader
You can get the transcript from any YouTube link. First, you have to install the given libraries. If you want to keep the video information like title, and description in the documents, then keep add_video_info=True Otherwise keep False.

```bash
# %pip install --upgrade --quiet  youtube-transcript-api
# %pip install --upgrade --quiet  pytube

from langchain_community.document_loaders import YoutubeLoader

loader = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=LAfrShnpVIk",
    add_video_info=False,
)

result = loader.load()
print("Without Video Info: {result}\n\n")

loader = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=LAfrShnpVIk",
    add_video_info=True,
)
result = loader.load()
print("With Video Info: {result}")
```

## Scraping data from URLs
We can scrape data from URLs in various ways such as HTMLloader, RecursiveUrlLoader, FireCrawl, and others.

The RecursiveUrlLoader is used to recursively scrape all the child links from a root URL and then convert the data into Documents.

```bash
# %pip install -qU langchain-community beautifulsoup4
#%pip install lxml
from langchain_community.document_loaders import RecursiveUrlLoader
import re
from bs4 import BeautifulSoup

# create recursiveurlloader instace with specific url
loader = RecursiveUrlLoader(
    "https://docs.python.org/3.9/",
    timeout=10,
    max_depth=2,
)

docs = loader.load()
print(len(docs))
print(docs[0].page_content)  # see the content

# function for removing html tag
def bs4_extractor(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    return re.sub(r"\n\n+", "\n\n", soup.text).strip()

content = bs4_extractor(docs[0].page_content)
print(f"After removing the html tags: {content}")

# define the extractor in the RecursiveUrlLoader Class
loader = RecursiveUrlLoader("https://docs.python.org/3.9/", extractor=bs4_extractor)
docs = loader.load()
print(docs[1].page_content)
```

## Custom Data Loader
If you don’t find any Data Loader class for your specific data type, then you can create a Custom Document Loader to convert your data into LLM-ready documents. Now create a custom document loader from Subclassing from **BaseLoader** that loads a file and creates a document from each line in the file. The document contains text and metadata. The BaseLoader class is used to convert the raw data into documents.

```bash
from typing import AsyncIterator, Iterator

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document


class CustomDocumentLoader(BaseLoader):
    """An example document loader that reads a file line by line."""

    def __init__(self, file_path: str) -> None:
        """Initialize the loader with a file path.

        Args:
            file_path: The path to the file to load.
        """
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:  # <-- Does not take any arguments
        """A lazy loader that reads a file line by line.

        When you're implementing lazy load methods, you should use a generator
        to yield documents one by one.
        """
        with open(self.file_path, encoding="utf-8") as f:
            line_number = 0
            for line in f:
                yield Document(
                    page_content=line,
                    metadata={"line_number": line_number, "source": self.file_path},
                )
                line_number += 1

# create a text file
with open("./meow.txt", "w", encoding="utf-8") as f:
    quality_content = "meow meow🐱 \n meow meow🐱 \n meow😻😻"
    f.write(quality_content)

# create instance of Custom Document Loader with the text file
loader = CustomDocumentLoader("./meow.txt")

# load the data and convert into Documents
for doc in loader.lazy_load():
    print()
    print(type(doc))
    print(doc)
```