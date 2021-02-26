# longevity-research-screening


Installing dependencies and running the simple model ...
For full model results run: $ python3 export_results.py full
For performance evaluation run: $ python3 evaluate_performance.py full

$ source ~/python-virtual-environments/longevity-screening/bin/activate

on Python 3.8.5


For full model:
sudo apt-get install default-jdk
sudo apt-get install ant

cd tools
git clone git@github.com:mimno/Mallet.git
cd Mallet
ant

For create databse:

https://chromedriver.chromium.org/downloads

or:
$ cd tools
$ LATEST_RELEASE=`curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE`
wget https://chromedriver.storage.googleapis.com/$LATEST_RELEASE/chromedriver_linux64.zip
unzip chromedriver_linux64.zip 
rm chromedriver_linux64.zip
