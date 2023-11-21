1. 同步命令可以参照我这个：nohup rsync -az --delete --no-motd --progress rsync://mirror.sg.gs/debian/pool/main/ /root/DATA/liuchengyue/debian_mirror &
2. nohup ... & 会后台执行命令，中间是rsync的命令。
3. ls-lR.gz 这个文件里有这个镜像站中所有资源的清单。
4. 整个镜像比较大，确保资源充足的前提下再全量复制。