# shopcart

除了基本的購物車商品，訂單，客戶資訊外，還包含購物優惠設定。

## Build

```sh
## 下載程式碼
git clone git@github.com:wyubin/shopcart.git
## 啟動安裝程式
sh shopcart/docker/install.sh
## 進入 container 中執行程式
docker exec -it shopcart ash
```

## Example

```sh
## DB initiate
python ./shopcart.py --init
## start...
python ./shopcart.py --user joe
```