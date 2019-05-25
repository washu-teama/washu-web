LOOP=$1
DJANGO_HOME=$2
# must do in root(sudo su)
while true; do
    sleep $LOOP &
    TIME=$(date +%H:%M:%S)
    printf '%s\n' $TIME
    
    source $DJANGO_HOME/../venv/bin/activate && python3 $DJANGO_HOME/scheduling/check_event.py >> $HOME/log
    wait # for sleep
done
