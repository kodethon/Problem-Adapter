src=$1
dest=$2
for assignment in $src/*; do
    assignment_name=$(basename -- "$assignment")
    echo $assignment
    sh assignment-descriptions.sh $assignment $dest
done
