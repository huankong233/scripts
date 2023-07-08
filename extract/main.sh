ext=".tar"
password=""
dir=""

cd $dir
for gz in *$ext; do extract $gz -P $password; done