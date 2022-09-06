FROM python

WORKDIR /app

# after first image, this will only install new dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# requirements.txt currently includes unneeded packages from archived files
# remove these files when closer to production

# copy all other files
COPY . /app

WORKDIR /app/Python_Trading/

