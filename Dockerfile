FROM latonaio/l4t:latest

# Definition of a Device & Service
ENV POSITION=Runtime \
    SERVICE=get-plc-backup-jtekt-with-samba \
    AION_HOME=/var/lib/aion

RUN mkdir ${AION_HOME}
WORKDIR ${AION_HOME}
# Setup Directoties
RUN mkdir -p \
    $POSITION/$SERVICE
WORKDIR ${AION_HOME}/$POSITION/$SERVICE/
ADD . .
RUN pip3 install --upgrade pip
RUN python3 setup.py install

CMD ["/bin/sh", "docker-entrypoint.sh"]
