#!/bin/sh
# Created at 2024/01/18 11:27
# @author huan_kong

ZSTD_EXE="https://ghproxy.com/https://github.com/facebook/zstd/releases/download/v1.5.5/zstd-v1.5.5-win64.zip"

download_file(){
	if [ -f $1 ]; then
		return 0
	fi
	echo "download $1 from $2"
	curl -o $1 -L $2
	if [ $? -ne 0 ]; then
		echo "download $1 failed!"
		exit 255
	fi
}

# select repo server
echo "Select MSYS2 repo server"
select tag in "official" "tsinghua" "USTC" "aliyun"; do
	case $tag in
		"USTC")
			REPOSERVER="https://mirrors.ustc.edu.cn/msys2/"
			break
			;;
		"tsinghua")
			REPOSERVER="https://mirrors.tuna.tsinghua.edu.cn/msys2/"
			break
			;;
		"aliyun")
			REPOSERVER="https://mirrors.aliyun.com/msys2/"
			break
			;;
		*)
			REPOSERVER="https://mirror.msys2.org/"
			break
			;;
	esac
done

REPO=$REPOSERVER"msys/x86_64/"
echo "Download from $REPOSERVER"

echo "Check version"
curl -L $REPO > repo.tmp
PACMAN=`cat repo.tmp | grep -oP "pacman-\d+\.\d+\.\d+.*?zst" | tail -n 1`
if [ -z $PACMAN ]; then
	echo "pacman not found"
	exit 255
fi
PACMAN_MIRRORS=`cat repo.tmp | grep -oP "pacman-mirrors.*?zst" | tail -n 1`
if [ -z $PACMAN_MIRRORS ]; then
	echo "pacman-mirrors not found"
	exit 255
fi
MSYS2_KEYRING=`cat repo.tmp | grep -oP "msys2-keyring.*?zst" | tail -n 1`
if [ -z $MSYS2_KEYRING ]; then
	echo "msys2-keyring not found"
	exit 255
fi
ZSTD=`cat repo.tmp | grep -oP "zstd.*?zst" | tail -n 1`
if [ -z $ZSTD ]; then
	echo "zstd not found"
	exit 255
fi

echo "find $PACMAN $PACMAN_MIRRORS $MSYS2_KEYRING $ZSTD" 

download_file "zstd-v1.5.5-win64.zip" $ZSTD_EXE
download_file $PACMAN $REPO$PACMAN
download_file $PACMAN_MIRRORS $REPO$PACMAN_MIRRORS
download_file $MSYS2_KEYRING $REPO$MSYS2_KEYRING
download_file $ZSTD $REPO$ZSTD

unzip -o ./zstd-v1.5.5-win64.zip "zstd-v1.5.5-win64/zstd.exe" -d .
./zstd-v1.5.5-win64/zstd.exe -f -d -o ${ZSTD%.zst} $ZSTD

tar -xvf ${ZSTD%.zst} -C /
tar -xvf $MSYS2_KEYRING -C /
tar -xvf $PACMAN -C /
tar -xvf $PACMAN_MIRRORS -C /


case $tag in
	"official")
		break
		;;
	*)
		sed -i "1i\Server = "$REPOSERVER"mingw/i686/" /etc/pacman.d/mirrorlist.mingw32
		sed -i "1i\Server = "$REPOSERVER"mingw/x86_64/" /etc/pacman.d/mirrorlist.mingw64
		sed -i "1i\Server = "$REPOSERVER"msys/\$arch/" /etc/pacman.d/mirrorlist.msys
		sed -i "1i\Server = "$REPOSERVER"mingw/ucrt64/" /etc/pacman.d/mirrorlist.ucrt64
		sed -i "1i\Server = "$REPOSERVER"mingw/clang32/" /etc/pacman.d/mirrorlist.clang32
		sed -i "1i\Server = "$REPOSERVER"mingw/clang64/" /etc/pacman.d/mirrorlist.clang64
		sed -i "1i\Server = "$REPOSERVER"mingw/\$repo/" /etc/pacman.d/mirrorlist.mingw
		break
		;;
esac

echo "Initialize pacman"

pacman-key --init
pacman-key --refresh-keys
pacman-key --populat msys2
pacman -Sydd --overwrite="*" --noconfirm ca-certificates
/git-bash.exe --login -i

pacman -Syu --overwrite="*" --noconfirm
pacman -Sydd --overwrite="*" --noconfirm pacman
pacman -Sydd --overwrite="*" --noconfirm pacman-mirrors
pacman -Sydd --overwrite="*" --noconfirm msys2-keyring
pacman -Sy --dbonly --noconfirm pacman
/git-bash.exe --login -i

printf "\n"
echo "Everything is ready, you can now enjoy pacman!"
