for assignment in $1/*; do
    echo $assignment
    sh assignment.sh $assignment
done
