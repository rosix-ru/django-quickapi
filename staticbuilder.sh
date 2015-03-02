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

CSS_SYM="../../static_src/css";
JS_SYM="../../static_src/js";
IMG_SYM="../../static_src/img";

VERSION_DIR="${DST_DIR}/${VERSION}";
CSS_DIR="${VERSION_DIR}/css";
JS_DIR="${VERSION_DIR}/js";
IMG_DIR="${VERSION_DIR}/img";


rm -R ${DST_DIR}
mkdir -p ${CSS_DIR} ${JS_DIR} ${IMG_DIR};


# symlinks for develop dirs
echo 'SYMLINKS FOR DEVELOP DIRS';
cd ${DST_DIR};
ln -s ${CSS_SYM} css;
ln -s ${JS_SYM} js;
ln -s ${IMG_SYM} img;
cd -;
echo '';


# CSS
echo "STARTS THE CREATION OF CSS FILES";
echo '';

lessc --source-map "${SRC_DIR}/css/quicktable.less" "${SRC_DIR}/css/quicktable.css"
echo "created ${SRC_DIR}/css/quicktable.css";

cp ${SRC_DIR}/css/quicktable.css ${CSS_DIR}/quicktable.css;
echo "copied ${CSS_DIR}/quicktable.css";

yui-compressor ${CSS_DIR}/quicktable.css \
            -o ${CSS_DIR}/quicktable.min.css --charset "utf-8";
echo "created ${CSS_DIR}/quicktable.min.js";
echo '';


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

cp -R ${SRC_DIR}/img/tables ${IMG_DIR}/tables;

#~ cp ${SRC_DIR}/img/*.ico ${IMG_DIR}/;
#~ cp ${SRC_DIR}/img/*.jpg ${IMG_DIR}/;
cp -v ${SRC_DIR}/img/*.png ${IMG_DIR}/;
cp -v ${SRC_DIR}/img/*.svg ${IMG_DIR}/;

echo '';

echo "ALL COMPLETED";

exit 0;
