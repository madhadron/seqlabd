import threading
import syslog
import Queue
import functools
import shutil

import refs
import queue_utils
import process

configuration_path = '/etc/seqlabd.conf'

def action(_):
    # All shared data structures for the daemon
    exit_event = threading.Event()
    config_ref = refs.Ref()
    inbox_queue = Queue.Queue()
    analysis_queue = Queue.Queue()
    summary_regen_queue = Queue.Queue()

    set_signal_handlers(config_ref, exit_event)

    # Initial read of the configuration file
    if os.path.exists(configuration_path):
        with open(configuration_path) as h:
            config_ref.put(read_configuration(h))
    else:
        syslog.syslog(syslog.LOG_ERR, 'Could not find configuration file at /etc/seqlabd.conf')
        exit(1)

    # Connect to MDX database (FIXME: actually connect...)
    mdx_conn = None

    # Attach behavior to queues

    # inbox_queue is monitored by batch_unique.
    fallthrough_fun = lambda k,p: shutil.move(p, config_ref['unmatched_path'].get())
    processing_fun = process(find_workup(mdx_conn),
                             requeue_n_times(inbox_queue, config_ref['max_retries'], fallthrough_fun),
                             process_pair(config_ref['share_path'], config['base_path'], analysis_queue, mdx_conn))
    threading.Thread(target=queue_utils.batched_unique,
                     args=(inbox_queue, processing_fun,
                           config_ref['batch_timeout'], exit_event)).start()
    
    threading.Thread(target=queue_utils.map_queue,
                     args=(analysis_queue, ..., exit_event)).start()

    threading.Thread(target=queue_utils.map_queue,
                     args=(summary_regen_queue, ..., exit_event)).start()

    # Set up inotify monitoring

    # Set up intermittent file enqueueing
