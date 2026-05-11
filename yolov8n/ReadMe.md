
python3.10 -m venv venv_3.10

sudo apt-get install libdmtx0b
sudo apt-get install libzbar0
pip install pylibdmtx opencv-python pyzbar

```
# Build own

wget https://github.com/dmtx/libdmtx/archive/refs/tags/v0.7.8.tar.gz

tar xvf v0.7.8.tar.gz

cd libdmtx-0.7.8

./autogen.sh

./configure CFLAGS="-O3 -march=native -mtune=native -flto -funroll-loops -ffast-math -DNDEBUG" CXXFLAGS="-O3 -march=native -mtune=native -flto -funroll-loops -ffast-math -DNDEBUG" --disable-static

make -j `nproc`
sudo make install

sudo apt install libopencv-dev

```