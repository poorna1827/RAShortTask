#conda create --name mini_wt -c conda-forge python=3.11

#conda activate mini_wt

#git config --global user.name tracykyle93
#
#git config --global user.email tracykyle93@gmail.com
#
#git config -l
#
#git clone git@github.com:tracykyle93/mini_wt.git

#cd ./mini_wt

#pip install -r requirements.txt

echo 'export PATH="$PATH:/btt/btr/"' >> ~/.bashrc

echo 'export PATH="$PATH:/btt/btr/backtrader/"' >> ~/.bashrc

echo 'export PATH="$PATH:/btt/btr/tests/"' >> ~/.bashrc && cd -

source ~/.bashrc

conda activate mini_wt

bash run_test.sh

