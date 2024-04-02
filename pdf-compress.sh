#!/bin/bash
# Compress slides to 144 px/inch

for infile in "${@}"; do
    echo "Processing ${infile}"

    tmpfile="$(mktemp -u).pdf"
    gs  -q -dNOPAUSE -dBATCH -dSAFER \
        -sDEVICE=pdfwrite \
        -dCompatibilityLevel=1.4 \
        -dPDFSETTINGS=/screen \
        -dEmbedAllFonts=true \
        -dSubsetFonts=true \
        -dColorImageDownsampleType=/Bicubic \
        -dColorImageResolution=144 \
        -dGrayImageDownsampleType=/Bicubic \
        -dGrayImageResolution=144 \
        -dMonoImageDownsampleType=/Bicubic \
        -dMonoImageResolution=144 \
        "-sOutputFile=${tmpfile}" \
        "${infile}"

    du -h "${infile}" "${tmpfile}"

    if [ "$(stat -f%z "${infile}")" -le "$(stat -f%z "${tmpfile}")" ]; then
        echo "Didn't shrink"
        continue
    fi

    mv "${tmpfile}" "${infile}"
done