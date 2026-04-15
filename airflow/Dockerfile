FROM astrocrpublic.azurecr.io/runtime:3.2-1

USER root
RUN pip install playwright
RUN playwright install-deps chromium

USER astro
RUN playwright install chromium