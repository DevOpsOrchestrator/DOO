# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: default
    type: stdout
    short_description: default Ansible screen output
    version_added: historical
    description:
        - This is the default output callback for ansible-playbook.
    extends_documentation_fragment:
      - default_callback
      - result_format_callback
    requirements:
      - set as stdout in configuration
'''


from ansible import constants as C
from ansible import context
from ansible.playbook.task_include import TaskInclude
from ansible.plugins.callback import CallbackBase
#from ansible.utils.color import colorize, hostcolor
from ansible.utils.fqcn import add_internal_fqcns

def colorize(lead, num, color):
    """ Print 'lead' = 'num' in 'color' """
    msg = u"%s=%-4s" % (lead, str(num))
    s = f'<span>{msg}</span>'
    if num != 0 and color is not None:
        s = f'<span style="color: {color}">{msg}</span>'
    return s


def hostcolor(host, stats, color=True):
    if color:
        if stats['failures'] != 0 or stats['unreachable'] != 0:
            msg = u"%-37s" % host
            return f'<span style="color: {C.COLOR_ERROR}">{msg}</span>'
        elif stats['changed'] != 0:
            msg = u"%-37s" % host
            return f'<span style="color: {C.COLOR_CHANGED}">{msg}</span>'
        else:
            msg =  u"%-37s" % host
            return f'<span style="color: {C.COLOR_OK}">{msg}</span>'
    msg = u"%-26s" % host
    return f'<span>{msg}</span>'

class CallbackModule(CallbackBase):

    '''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'default'

    def __init__(self):

        self._play = None
        self._last_task_banner = None
        self._last_task_name = None
        self._task_type_cache = {}
        self._return = []
        super(CallbackModule, self).__init__()

    def v2_runner_on_failed(self, result, ignore_errors=False):

        host_label = self.host_label(result)
        self._clean_results(result._result, result._task.action)

        if self._last_task_banner != result._task._uuid:
            self._print_task_banner(result._task)

        self._handle_exception(result._result, use_stderr=self.get_option('display_failed_stderr'))
        self._handle_warnings(result._result)

        if result._task.loop and 'results' in result._result:
            self._process_items(result)

        else:
            if self.get_option('show_task_path_on_failure'):
                self._print_task_path(result._task)
            msg = "fatal: [%s]: FAILED! => %s" % (host_label, self._dump_results(result._result))
            self._return.append(f'<div><span style="color: {C.COLOR_ERROR}">{msg}</span></div>')
            #self._display.display(msg, color=C.COLOR_ERROR, stderr=self.get_option('display_failed_stderr'))

        if ignore_errors:
            self._return.append(f'<div><span style="color: {C.COLOR_SKIP}">...ignoring</span></div>')
            #self._display.display("...ignoring", color=C.COLOR_SKIP)

    def v2_runner_on_ok(self, result):

        host_label = self.host_label(result)

        if isinstance(result._task, TaskInclude):
            if self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)
            return
        elif result._result.get('changed', False):
            if self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)

            msg = "changed: [%s]" % (host_label,)
            color = C.COLOR_CHANGED
        else:
            if not self.get_option('display_ok_hosts'):
                return

            if self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)

            msg = "ok: [%s]" % (host_label,)
            color = C.COLOR_OK

        self._handle_warnings(result._result)

        if result._task.loop and 'results' in result._result:
            self._process_items(result)
        else:
            self._clean_results(result._result, result._task.action)

            #if self._run_is_verbose(result):
            msg += " => %s" % (self._dump_results(result._result),)
            #self._display.display(msg, color=color)
            self._return.append(f'<div><span style="color: {color}">{msg}</span></div>')

    def v2_runner_on_skipped(self, result):

        if self.get_option('display_skipped_hosts'):

            self._clean_results(result._result, result._task.action)

            if self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)

            if result._task.loop is not None and 'results' in result._result:
                self._process_items(result)

            msg = "skipping: [%s]" % result._host.get_name()
            #if self._run_is_verbose(result):
            msg += " => %s" % self._dump_results(result._result)
            #self._display.display(msg, color=C.COLOR_SKIP)
            self._return.append(f'<div><span style="color: {C.COLOR_SKIP}">{msg}</span></div>')

    def v2_runner_on_unreachable(self, result):
        if self._last_task_banner != result._task._uuid:
            self._print_task_banner(result._task)

        host_label = self.host_label(result)
        msg = "fatal: [%s]: UNREACHABLE! => %s" % (host_label, self._dump_results(result._result))
        #self._display.display(msg, color=C.COLOR_UNREACHABLE, stderr=self.get_option('display_failed_stderr'))
        self._return.append(f'<div><span style="color: {C.COLOR_UNREACHABLE}">{msg}</span></div>')
        

        if result._task.ignore_unreachable:
            #self._display.display("...ignoring", color=C.COLOR_SKIP)
            self._return.append(f'<div><span style="color: {C.COLOR_SKIP}">...ignoring</span></div>')

    def v2_playbook_on_no_hosts_matched(self):
        #self._display.display("skipping: no hosts matched", color=C.COLOR_SKIP)
        self._return.append(f'<div><span style="color: {C.COLOR_SKIP}">skipping: no hosts matched</span></div>')

    def v2_playbook_on_no_hosts_remaining(self):
        self._display.banner("NO MORE HOSTS LEFT")
        self._return.append(f'<div><span>NO MORE HOSTS LEFT/span></div>')


    def v2_playbook_on_task_start(self, task, is_conditional):
        self._task_start(task, prefix='TASK')

    def _task_start(self, task, prefix=None):
        # Cache output prefix for task if provided
        # This is needed to properly display 'RUNNING HANDLER' and similar
        # when hiding skipped/ok task results
        if prefix is not None:
            self._task_type_cache[task._uuid] = prefix

        # Preserve task name, as all vars may not be available for templating
        # when we need it later
        if self._play.strategy in add_internal_fqcns(('free', 'host_pinned')):
            # Explicitly set to None for strategy free/host_pinned to account for any cached
            # task title from a previous non-free play
            self._last_task_name = None
        else:
            self._last_task_name = task.get_name().strip()

            # Display the task banner immediately if we're not doing any filtering based on task result
            if self.get_option('display_skipped_hosts') and self.get_option('display_ok_hosts'):
                self._print_task_banner(task)

    def _print_task_banner(self, task):
        # args can be specified as no_log in several places: in the task or in
        # the argument spec.  We can check whether the task is no_log but the
        # argument spec can't be because that is only run on the target
        # machine and we haven't run it thereyet at this time.
        #
        # So we give people a config option to affect display of the args so
        # that they can secure this if they feel that their stdout is insecure
        # (shoulder surfing, logging stdout straight to a file, etc).
        args = ''
        if not task.no_log and C.DISPLAY_ARGS_TO_STDOUT:
            args = u', '.join(u'%s=%s' % a for a in task.args.items())
            args = u' %s' % args

        prefix = self._task_type_cache.get(task._uuid, 'TASK')

        # Use cached task name
        task_name = self._last_task_name
        if task_name is None:
            task_name = task.get_name().strip()

        if task.check_mode and self.get_option('check_mode_markers'):
            checkmsg = " [CHECK MODE]"
        else:
            checkmsg = ""
        #self._display.banner(u"%s [%s%s]%s" % (prefix, task_name, args, checkmsg))
        self._return.append(f'<div><span>{prefix}[{task_name}{args}]{checkmsg}</span></div>')

        if self._display.verbosity >= 2:
            self._print_task_path(task)

        self._last_task_banner = task._uuid

    def v2_playbook_on_cleanup_task_start(self, task):
        self._task_start(task, prefix='CLEANUP TASK')

    def v2_playbook_on_handler_task_start(self, task):
        self._task_start(task, prefix='RUNNING HANDLER')

    def v2_runner_on_start(self, host, task):
        if self.get_option('show_per_host_start'):
            #self._display.display(" [started %s on %s]" % (task, host), color=C.COLOR_OK)
            self._return.append(f'<div><span style="color: {C.COLOR_OK}"> [started {task} on {host}]</span></div>')

    def v2_playbook_on_play_start(self, play):
        name = play.get_name().strip()
        if play.check_mode and self.get_option('check_mode_markers'):
            checkmsg = " [CHECK MODE]"
        else:
            checkmsg = ""
        if not name:
            msg = u"PLAY%s" % checkmsg
        else:
            msg = u"PLAY [%s]%s" % (name, checkmsg)

        self._play = play

        #self._display.banner(msg)
        self._return.append(f'<div><span>{msg}</span></div>')

    def v2_on_file_diff(self, result):
        if result._task.loop and 'results' in result._result:
            for res in result._result['results']:
                if 'diff' in res and res['diff'] and res.get('changed', False):
                    diff = self._get_diff(res['diff'])
                    if diff:
                        if self._last_task_banner != result._task._uuid:
                            self._print_task_banner(result._task)
                        #self._display.display(diff)
                        self._return.append(f'<div><span>{diff}</span></div>')
        elif 'diff' in result._result and result._result['diff'] and result._result.get('changed', False):
            diff = self._get_diff(result._result['diff'])
            if diff:
                if self._last_task_banner != result._task._uuid:
                    self._print_task_banner(result._task)
                #self._display.display(diff)
                self._return.append(f'<div><span>{diff}</span></div>')

    def v2_runner_item_on_ok(self, result):

        host_label = self.host_label(result)
        if isinstance(result._task, TaskInclude):
            return
        elif result._result.get('changed', False):
            if self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)

            msg = 'changed'
            color = C.COLOR_CHANGED
        else:
            if not self.get_option('display_ok_hosts'):
                return

            if self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)

            msg = 'ok'
            color = C.COLOR_OK

        msg = "%s: [%s] => (item=%s)" % (msg, host_label, self._get_item_label(result._result))
        self._clean_results(result._result, result._task.action)
        #if self._run_is_verbose(result):
        msg += " => %s" % self._dump_results(result._result)
        #self._display.display(msg, color=color)
        self._return.append(f'<div><span style="color: {color}">{msg}</span></div>')

    def v2_runner_item_on_failed(self, result):
        if self._last_task_banner != result._task._uuid:
            self._print_task_banner(result._task)

        host_label = self.host_label(result)
        self._clean_results(result._result, result._task.action)
        self._handle_exception(result._result, use_stderr=self.get_option('display_failed_stderr'))

        msg = "failed: [%s]" % (host_label,)
        self._handle_warnings(result._result)
        #self._display.display(
        #    msg + " (item=%s) => %s" % (self._get_item_label(result._result), self._dump_results(result._result)),
        #    color=C.COLOR_ERROR,
        #    stderr=self.get_option('display_failed_stderr')
        #)
        self._return.append(f'<div><span style="color: {C.COLOR_ERROR}">{msg} (item={self._get_item_label(result._result)}) => {self._dump_results(result._result)}"</span></div>')

    def v2_runner_item_on_skipped(self, result):
        if self.get_option('display_skipped_hosts'):
            if self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)

            self._clean_results(result._result, result._task.action)
            msg = "skipping: [%s] => (item=%s) " % (result._host.get_name(), self._get_item_label(result._result))
            #if self._run_is_verbose(result):
            msg += " => %s" % self._dump_results(result._result)
            #self._display.display(msg, color=C.COLOR_SKIP)
            self._return.append(f'<div><span style="color: {C.COLOR_SKIP}">{msg}</span></div>')


    def v2_playbook_on_include(self, included_file):
        msg = 'included: %s for %s' % (included_file._filename, ", ".join([h.name for h in included_file._hosts]))
        label = self._get_item_label(included_file._vars)
        if label:
            msg += " => (item=%s)" % label
        #self._display.display(msg, color=C.COLOR_SKIP)
        self._return.append(f'<div><span style="color: {C.COLOR_SKIP}">{msg}</span></div>')

    def v2_playbook_on_stats(self, stats):
        #self._display.banner("PLAY RECAP")
        self._return.append(f'<div><span>PLAY RECAP</span></div>')

        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)

            # self._display.display(
            #     u"%s : %s %s %s %s %s %s %s" % (
            #         hostcolor(h, t),
            #         colorize(u'ok', t['ok'], C.COLOR_OK),
            #         colorize(u'changed', t['changed'], C.COLOR_CHANGED),
            #         colorize(u'unreachable', t['unreachable'], C.COLOR_UNREACHABLE),
            #         colorize(u'failed', t['failures'], C.COLOR_ERROR),
            #         colorize(u'skipped', t['skipped'], C.COLOR_SKIP),
            #         colorize(u'rescued', t['rescued'], C.COLOR_OK),
            #         colorize(u'ignored', t['ignored'], C.COLOR_WARN),
            #     ),
            #     screen_only=True
            # )
            msg = u"%s : %s %s %s %s %s %s %s" % (
                    hostcolor(h, t),
                    colorize(u'ok', t['ok'], C.COLOR_OK),
                    colorize(u'changed', t['changed'], C.COLOR_CHANGED),
                    colorize(u'unreachable', t['unreachable'], C.COLOR_UNREACHABLE),
                    colorize(u'failed', t['failures'], C.COLOR_ERROR),
                    colorize(u'skipped', t['skipped'], C.COLOR_SKIP),
                    colorize(u'rescued', t['rescued'], C.COLOR_OK),
                    colorize(u'ignored', t['ignored'], C.COLOR_WARN),
                )
            self._return.append(f'<div><span>{msg}</span></div>')


            # self._display.display(
            #     u"%s : %s %s %s %s %s %s %s" % (
            #         hostcolor(h, t, False),
            #         colorize(u'ok', t['ok'], None),
            #         colorize(u'changed', t['changed'], None),
            #         colorize(u'unreachable', t['unreachable'], None),
            #         colorize(u'failed', t['failures'], None),
            #         colorize(u'skipped', t['skipped'], None),
            #         colorize(u'rescued', t['rescued'], None),
            #         colorize(u'ignored', t['ignored'], None),
            #     ),
            #     log_only=True
            # )
            msg = u"%s : %s %s %s %s %s %s %s" % (
                    hostcolor(h, t, False),
                    colorize(u'ok', t['ok'], None),
                    colorize(u'changed', t['changed'], None),
                    colorize(u'unreachable', t['unreachable'], None),
                    colorize(u'failed', t['failures'], None),
                    colorize(u'skipped', t['skipped'], None),
                    colorize(u'rescued', t['rescued'], None),
                    colorize(u'ignored', t['ignored'], None),
                )
            
            #self._return.append(f'<div><span>{msg}</span></div>')


        #self._display.display("", screen_only=True)
        self._return.append(f'<div><span></span></div>')

        # print custom stats if required
        if stats.custom and self.get_option('show_custom_stats'):
            self._display.banner("CUSTOM STATS: ")
            # per host
            # TODO: come up with 'pretty format'
            for k in sorted(stats.custom.keys()):
                if k == '_run':
                    continue
                #self._display.display('\t%s: %s' % (k, self._dump_results(stats.custom[k], indent=1).replace('\n', '')))
                msg = '\t%s: %s' % (k, self._dump_results(stats.custom[k], indent=1).replace('\n', ''))
                self._return.append(f'<div><span>{msg}</span></div>')

            # print per run custom stats
            if '_run' in stats.custom:
                #self._display.display("", screen_only=True)
                self._return.append(f'<div><span></span></div>')
                #self._display.display('\tRUN: %s' % self._dump_results(stats.custom['_run'], indent=1).replace('\n', ''))
                msg = '\tRUN: %s' % self._dump_results(stats.custom['_run'], indent=1).replace('\n', '')
                self._return.append(f'<div><span>{msg}</span></div>')
            #self._display.display("", screen_only=True)
            self._return.append(f'<div><span></span></div>')

        if context.CLIARGS['check'] and self.get_option('check_mode_markers'):
            #self._display.banner("DRY RUN")
            self._return.append(f'<div><span>DRY RUN</span></div>')

    def v2_playbook_on_start(self, playbook):
        #if self._display.verbosity > 1:
        from os.path import basename
        #self._display.banner("PLAYBOOK: %s" % basename(playbook._file_name))
        self._return.append(f'<div><span>PLAYBOOK: {basename(playbook._file_name)}</span></div>')
            

        # show CLI arguments
        #if self._display.verbosity > 3:
        if context.CLIARGS.get('args'):
            #self._display.display('Positional arguments: %s' % ' '.join(context.CLIARGS['args']),
            #                      color=C.COLOR_VERBOSE, screen_only=True)
            msg = 'Positional arguments: %s' % ' '.join(context.CLIARGS['args'])
            self._return.append(f'<div><span style="color: {C.COLOR_VERBOSE}">{msg}</span></div>')

        for argument in (a for a in context.CLIARGS if a != 'args'):
            val = context.CLIARGS[argument]
            if val:
                #self._display.display('%s: %s' % (argument, val), color=C.COLOR_VERBOSE, screen_only=True)
                msg = '%s: %s' % (argument, val)
                self._return.append(f'<div><span style="color: {C.COLOR_VERBOSE}">{msg}</span></div>')

        if context.CLIARGS['check'] and self.get_option('check_mode_markers'):
            #self._display.banner("DRY RUN")
            self._return.append(f'<div><span>DRY RUN</span></div>')

    def v2_runner_retry(self, result):
        task_name = result.task_name or result._task
        host_label = self.host_label(result)
        msg = "FAILED - RETRYING: [%s]: %s (%d retries left)." % (host_label, task_name, result._result['retries'] - result._result['attempts'])
        #if self._run_is_verbose(result, verbosity=2):
        msg += "Result was: %s" % self._dump_results(result._result)
        #self._display.display(msg, color=C.COLOR_DEBUG)
        self._return.append(f'<div><span style="color: {C.COLOR_DEBUG}">{msg}</span></div>')

    def v2_runner_on_async_poll(self, result):
        host = result._host.get_name()
        jid = result._result.get('ansible_job_id')
        started = result._result.get('started')
        finished = result._result.get('finished')
        # self._display.display(
        #     'ASYNC POLL on %s: jid=%s started=%s finished=%s' % (host, jid, started, finished),
        #     color=C.COLOR_DEBUG
        # )
        msg = 'ASYNC POLL on %s: jid=%s started=%s finished=%s' % (host, jid, started, finished)
        self._return.append(f'<div><span style="color: {C.COLOR_DEBUG}">{msg}</span></div>')

    def v2_runner_on_async_ok(self, result):
        host = result._host.get_name()
        jid = result._result.get('ansible_job_id')
        #self._display.display("ASYNC OK on %s: jid=%s" % (host, jid), color=C.COLOR_DEBUG)
        msg = "ASYNC OK on %s: jid=%s" % (host, jid)
        self._return.append(f'<div><span style="color: {C.COLOR_DEBUG}">{msg}</span></div>')

    def v2_runner_on_async_failed(self, result):
        host = result._host.get_name()

        # Attempt to get the async job ID. If the job does not finish before the
        # async timeout value, the ID may be within the unparsed 'async_result' dict.
        jid = result._result.get('ansible_job_id')
        if not jid and 'async_result' in result._result:
            jid = result._result['async_result'].get('ansible_job_id')
        #self._display.display("ASYNC FAILED on %s: jid=%s" % (host, jid), color=C.COLOR_DEBUG)
        msg = "ASYNC FAILED on %s: jid=%s" % (host, jid)
        self._return.append(f'<div><span style="color: {C.COLOR_DEBUG}">{msg}</span></div>')

    def v2_playbook_on_notify(self, handler, host):
        #if self._display.verbosity > 1:
        #self._display.display("NOTIFIED HANDLER %s for %s" % (handler.get_name(), host), color=C.COLOR_VERBOSE, screen_only=True)
        msg = "NOTIFIED HANDLER %s for %s" % (handler.get_name(), host)
        self._return.append(f'<div><span style="color: {C.COLOR_VERBOSE}">{msg}</span></div>')
