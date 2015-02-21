#!/usr/bin/env bash

if [ -f 'quickapi/__init__.py' ]
then
    VERSION=$(python -c 'import quickapi; print(quickapi.get_version());');
else
    echo 'This script must be run from it directory!';
    exit 1;
fi;


echo "QuickAPI version: ${VERSION}";
echo '';

SRC_DIR="quickapi/static_src";
DST_DIR="quickapi/static/quickapi";

VERSION_DIR="${DST_DIR}/${VERSION}";
#~ CSS_DIR="${VERSION_DIR}/css";
JS_DIR="${VERSION_DIR}/js";
IMG_DIR="${VERSION_DIR}/img";

rm -R ${DST_DIR}
mkdir -p ${JS_DIR} ${IMG_DIR};


# JS
echo "STARTS THE CREATION OF JS FILES";
echo '';

cp ${SRC_DIR}/js/jquery.quickapi.js ${JS_DIR}/jquery.quickapi.js;
echo "copied ${JS_DIR}/jquery.quickapi.js";

yui-compressor ${JS_DIR}/jquery.quickapi.js \
            -o ${JS_DIR}/jquery.quickapi.min.js --charset "utf-8";
echo "created ${JS_DIR}/jquery.quickapi.min.js";
echo '';

cp ${SRC_DIR}/js/jquery.quicktable.js ${JS_DIR}/jquery.quicktable.js;
echo "copied ${JS_DIR}/jquery.quicktable.js";

yui-compressor ${JS_DIR}/jquery.quicktable.js \
            -o ${JS_DIR}/jquery.quicktable.min.js --charset "utf-8";
echo "created ${JS_DIR}/jquery.quicktable.min.js";
echo '';

cat ${SRC_DIR}/js/jquery.quickapi.js > ${JS_DIR}/jquery.quickapi.full.js;
cat ${SRC_DIR}/js/jquery.quicktable.js >> ${JS_DIR}/jquery.quickapi.full.js;
echo "created ${JS_DIR}/jquery.quickapi.full.js";

yui-compressor ${JS_DIR}/jquery.quickapi.full.js \
            -o ${JS_DIR}/jquery.quickapi.full.min.js --charset "utf-8";
echo "created ${JS_DIR}/jquery.quickapi.full.min.js";
echo '';

# IMG
echo "STARTS THE COPYING IMAGE FILES";
echo '';

#~ cp ${SRC_DIR}/img/*.ico ${IMG_DIR}/;
#~ cp ${SRC_DIR}/img/*.jpg ${IMG_DIR}/;
cp -v ${SRC_DIR}/img/*.png ${IMG_DIR}/;
cp -v ${SRC_DIR}/img/*.svg ${IMG_DIR}/;

echo '';

echo "ALL COMPLETED";

exit 0;
