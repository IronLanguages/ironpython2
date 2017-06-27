FROM mono:4.8
RUN apt-get update && apt-get install -y make
ADD . /home/travis/build/IronLanguages/ironpython2
WORKDIR /home/travis/build/IronLanguages/ironpython2
CMD [ "make", "test-all" ]
