# 安裝 python3、git、virtualenv
sudo apt update
sudo apt install python3-pip
sudo apt install git

pip3 install virtualenv

# 下載程式碼
git clone https://github.com/aaron1aaron2/Land-price-predict-based-on-transaction-records.git
cd Land-price-predict-based-on-transaction-records

# 建立環境
python3 -m virtualenv .venv

# 進入環境
source .venv/bin/activate