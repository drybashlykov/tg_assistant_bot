from med_reminder import start_med_repeater
from horoscope import horoscope
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

job_dict = {"med_reminder": start_med_repeater,
            "horoscope": horoscope}

def get_cron_trigger(task_settings):
    t_s = task_settings
    print(task_settings)
    trigger = CronTrigger(year="*", month="*", day="*",
                            hour=t_s["hour"], minute=t_s["minute"],
                            second="0")
    return trigger

def get_interval_trigger(task_settings):
    t_s = task_settings
    interval = timedelta(seconds=t_s["seconds"]) 
    print(task_settings)
    trigger = DateTrigger(datetime.now() + interval)
    return trigger

def add_task(scheduler, trigger, task, config, linked_objects):
    job_func = job_dict[task]
    #job_func = test_job_func
    scheduler.add_job(  
        job_func,
        trigger=trigger,
        args=[config, linked_objects],
        name=task,
    )
    return 0

def setup_scheduler(config, linked_objects):
    scheduler = BackgroundScheduler(job_defaults={'misfire_grace_time': 15*60})
    
    if config["scheduling"]["mode"] == "normal":
        for task in config["scheduling"]["tasks"]:
            task_settings = config["scheduling"]["tasks"][task]
            trigger = get_cron_trigger(task_settings)
            add_task(scheduler, trigger, task, config, linked_objects)

    if config["scheduling"]["mode"] == "testing":
        for task in config["scheduling"]["tasks"]:
            task_settings = config["scheduling"]["tasks"][task]
            trigger = get_interval_trigger(task_settings)
            add_task(scheduler, trigger, task, config, linked_objects)

    # med_trigger = CronTrigger(
    #     year="*", month="*", day="*", hour="9", minute="50", second="0"
    # )

    # horoscope_trigger = CronTrigger(
    #     year="*", month="*", day="*", hour="7", minute="30", second="0"
    # )

    # scheduler.add_job(  
    #     start_med_repeater,
    #     trigger=med_trigger,
    #     args=[],
    #     name="med reminder",
    # )

    # scheduler.add_job(  
    #     horoscope,
    #     trigger=horoscope_trigger,
    #     args=[],
    #     name="horoscope",
    # )

    return scheduler