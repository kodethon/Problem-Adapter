for category in $1/*; do
    src_folder=$category/python

    # If the folder exists...
    if [ -d "$src_folder" ]; then
        for dir in $src_folder/*; do
            echo "Processing $dir..."

            dirname=$(basename -- "$dir")
            sh adapt-one.sh $dir/$dirname.py
        done
    fi
done
