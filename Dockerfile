FROM --platform=linux/amd64 python:3.10

WORKDIR /app

RUN pip install --no-cache-dir \
    PyMuPDF==1.23.22 \
    scikit-learn==1.4.1.post1 \
    numpy==1.24.4


COPY process_pdfs.py .
COPY Collection_1/ Collection_1/
COPY Collection_2/ Collection_2/
COPY Collection_3/ Collection_3/

CMD ["python", "process_pdfs.py"] 