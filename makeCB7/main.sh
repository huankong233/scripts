# 这是要压缩的目录的名称，您可以修改成其他名称
folder=a

for dir in $folder/*; do
    7z a -t7z -r "${dir##*/}.cb7" "$dir"
done
