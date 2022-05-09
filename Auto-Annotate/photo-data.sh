#!/bin/bash -e

# python /home/nos/code-school/bachelor-ikt300/Auto-Annotate/annotate.py

for filename in /home/nos/code-school/bachelor-ikt300/cutout/Photo-data/*
do
  # python annotate.py annotateCustom --image_directory=/home/nos/code-school/bachelor-ikt300/cutout/Photo-data/${filename} --label=frog_stomach --weights=frog_stomach_2.h5 --displayMaskedImages=False
python /home/nos/code-school/bachelor-ikt300/Auto-Annotate/annotate.py annotateCustom --image_directory=${filename} --label=frog_stomach --weights=frog_stomach_2.h5 --displayMaskedImages=False
done
