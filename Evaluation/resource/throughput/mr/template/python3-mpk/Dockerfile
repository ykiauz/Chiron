FROM openfaas/of-watchdog:0.7.7 as watchdog
FROM python:3.7-slim-buster

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

ARG ADDITIONAL_PACKAGE
# Alternatively use ADD https:// (which will not be cached by Docker builder)

RUN apt-get -qy update --fix-missing && apt-get -qy install gcc make ${ADDITIONAL_PACKAGE}

# Add non root user
RUN addgroup --system app && adduser app --system --ingroup app
RUN chown app /home/app

USER app

ENV PATH=$PATH:/home/app/.local/bin

WORKDIR /home/app/

COPY index.py           .
COPY requirements.txt   .
COPY mpkmemalloc.cpython-37m-x86_64-linux-gnu.so .
COPY mpkmemalloc-1.0.0-py3.7.egg-info .

USER root
RUN pip install -r requirements.txt

RUN cp mpkmemalloc.cpython-37m-x86_64-linux-gnu.so /usr/local/lib/python3.7/site-packages/
RUN cp mpkmemalloc-1.0.0-py3.7.egg-info /usr/local/lib/python3.7/site-packages/

#build function directory and install user specified componenets.
USER app

RUN mkdir -p function
RUN touch ./function/__init__.py
WORKDIR /home/app/function/
COPY function/requirements.txt	.
RUN pip install --user -r requirements.txt

WORKDIR /home/app/

#install function code
USER root

COPY function   function
RUN chown -R app:app ./

#configure WSGI server and healthcheck
USER app

ENV fprocess="python index.py"

ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:5000"

HEALTHCHECK --interval=5s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
