FROM python
ADD ./requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 5000
ADD osmlodz/main.py .
ADD osmlodz/templates templates
CMD ./main.py
