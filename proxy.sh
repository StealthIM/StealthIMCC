while true;do
    echo "Starting proxy..."
    ncat -l -p 11450 --sh-exec "ncat --crlf 127.0.0.1 11451" -o proxy.log
done