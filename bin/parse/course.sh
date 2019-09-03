for assignment in $1/*; do
    echo $assignment
    sh parse-assignment.sh $assignment
done
