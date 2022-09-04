FROM python

WORKDIR /

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# requirements.txt currently includes unneeded packages from archived files
# remove these files when closer to production

COPY . .