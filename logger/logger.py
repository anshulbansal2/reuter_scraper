import logging
import inspect
import string
import sys


"""
This is a custom logging framework. This is a wrapper
around Python's native logging API. This framework helps us to create
properly structured logs without requiring much developer effort. It
generates the following fields in the logs separated by '\\t\\x01':

 - log_type:

   A label for the component generating the logs, e.g. "stockpricing", "fd" etc.
   .


 - bucket:

   A label for the bucket for grouping the generated logs, e.g.
   "ticketchanger". Defalt value is "UNKNOWN".


 - stage:

   A label for a particular stage in a multi stage user flow, e.g. any of the funnel step of a
   service
   Using proper stage labels will help identifying drops in similar
   multistage workflows by analyzing the logs.

   Default value is the name of the calling function/method.


 - message:

   Developer message. Default value is "".


 - caller:

   Dot separated name of calling function/method. Automatically generated.


 - client tracking id:

   A unique tracker id for a client. Automatically generated.


Most of the fields are auto generated along with ability to customize
some of them if needed: log_type, bucket, stage.

Sample usage:

>>> from common.logger import Logger
>>> logger = Logger()
>>> logger_stats = Logger(logger="serviceLoggerSTATS")
>>> logger.info("Foobar")
>>> logger.debug("Foobar", bucket="blah")
>>> logger.info("Foobar", bucket="ticketchanger", stage="form rendered")
>>> logger_stats.critical("Foobar")
>>> logger_stats.critical("Foobar", log_type="blah", bucket="ticketchanger",
... stage="form rendered")

"""


class Logger(object):
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    """
    Initialize Logger instance.

    Args:
        log_type: A string for the label of the component generating logs,
                  e.g. 'flight', 'bus', etc.
        logger: A string for the name of logger to use.
    """
    def __init__(self, log_type="", logger='INDMoneyLogs'):
        self.log_type = 'reuter_scraper'
        self._logger_name = logger
        self._logger = logging.getLogger(logger)


    """
    Safely encode to ASCII string.

    Args:
        item: Any object, string, unicode.

    Returns:
        An ASCII string representation for item.
    """
    def _safe_encode(self, item):
        item = str(item)
        return item


    """
    Generates log message.

    Returns '\\t\\x01' separted log message.
    """
    def _format_log_message(self, message="", identifier="",
            extra_message="", client_id="", log_type="", bucket="", stage=""):
        log_type = log_type or self.log_type
        bucket = bucket or "UNKNOWN"
        caller = caller_name()
        if not log_type:
            log_type = caller.split('.')[0]
        separator = '\t\x01'
        log_message = "\t".join(
            [i for i in (
                self._safe_encode(message), self._safe_encode(identifier),
                self._safe_encode(extra_message)) if i])
        if not stage:
            stage = caller.split('.')[-1]
        log_message = separator.join(
            [self._safe_encode(log_type), self._safe_encode(bucket),
             self._safe_encode(client_id),
             self._safe_encode(stage), log_message,
             self._safe_encode(caller)])
        return log_message


    """
    Generates INFO log.

    Args:
        message: A string for developer message. It's mandatory and can
                 be supplied as the first argument or a keyword
                 argument.
        identifier: Deprecated.
        extra_message: Deprecated,
        log_type: A string for log type.
        bucket: A string for log bucket. It's mandatory if you want
                your logs to be grouped properly.
        exc_info: A boolean.
        stage: A string for log stage.
    """
    def info(self, message="", identifier="",
             extra_message="", client_id="", exc_info=False, bucket="", stage=""):

        try:
            log_message = self._format_log_message(
                    message=message, identifier=identifier,
                    extra_message=extra_message, client_id=client_id, log_type=self.log_type,
                    bucket=bucket, stage=stage)
            self._logger.info(log_message, exc_info=exc_info)
        except Exception as e:
            self._logger.info("CommonLoggerError: %s" % e, exc_info=True)


    """
    Generates CRITICAL log.

    Args:
        message: A string for developer message. It's mandatory and can
                 be supplied as the first argument or a keyword
                 argument.
        identifier: Deprecated.
        extra_message: Deprecated,
        log_type: A string for log type.
        bucket: A string for log bucket. It's mandatory if you want
                your logs to be grouped properly.
        exc_info: A boolean.
        stage: A string for log stage.
    """
    def critical(self, message="", identifier="",
             extra_message="", client_id="", exc_info=False, bucket="", stage=""):
        try:
            log_message = self._format_log_message(
                    message=message, identifier=identifier,
                    extra_message=extra_message, client_id=client_id, log_type=self.log_type,
                    bucket=bucket, stage=stage)
            self._logger.critical(log_message, exc_info=exc_info)
        except Exception as e:
            self._logger.info("CommonLoggerError: %s" % e, exc_info=True)

    """
    Generates DEBUG log.

    Args:
        message: A string for developer message. It's mandatory and can
                 be supplied as the first argument or a keyword
                 argument.
        identifier: Deprecated.
        extra_message: Deprecated,
        log_type: A string for log type.
        bucket: A string for log bucket. It's mandatory if you want
                your logs to be grouped properly.
        error: Deprecated.
        exc_info: A boolean.
        stage: A string for log stage.
    """
    def debug(self, message="", identifier="",
             extra_message="", client_id="", exc_info=False, bucket="", stage=""):
        try:
            log_message = self._format_log_message(
                    message=message, identifier=identifier,
                    extra_message=extra_message, client_id=client_id, log_type=self.log_type,
                    bucket=bucket, stage=stage)
            self._logger.debug(log_message, exc_info=exc_info)
        except Exception as e:
            self._logger.info("CommonLoggerError: %s" % e, exc_info=True)

    """
    Generates ERROR log.

    Args:
        message: A string for developer message. It's mandatory and can
                 be supplied as the first argument or a keyword
                 argument.
        identifier: Deprecated.
        extra_message: Deprecated,
        log_type: A string for log type.
        bucket: A string for log bucket. It's mandatory if you want
                your logs to be grouped properly.
        error: Deprecated.
        exc_info: A boolean.
        stage: A string for log stage.
    """
    def error(self, message="", identifier="",
             extra_message="", client_id="", exc_info=False, bucket="", stage=""):
        try:
            log_message = self._format_log_message(
                    message=message, identifier=identifier,
                    extra_message=extra_message, client_id=client_id, log_type=self.log_type,
                    bucket=bucket, stage=stage)
            self._logger.error(log_message, exc_info=exc_info)
        except Exception as e:
            self._logger.info("CommonLoggerError: %s" % e, exc_info=True)


    """
    Generates WARNING log.

    Args:
        message: A string for developer message. It's mandatory and can
                 be supplied as the first argument or a keyword
                 argument.
        identifier: Deprecated.
        extra_message: Deprecated,
        log_type: A string for log type.
        bucket: A string for log bucket. It's mandatory if you want
                your logs to be grouped properly.
        error: Deprecated.
        exc_info: A boolean.
        stage: A string for log stage.
    """
    def warning(self, message="", identifier="",
             extra_message="", client_id="", exc_info=False, bucket="", stage=""):
        try:
            log_message = self._format_log_message(
                    message=message, identifier=identifier,
                    extra_message=extra_message, client_id=client_id, log_type=self.log_type,
                    bucket=bucket, stage=stage)
            self._logger.warning(log_message, exc_info=exc_info)
        except Exception as e:
            self._logger.info("CommonLoggerError: %s" % e, exc_info=True)


"""
Get a name of a caller in the format module.class.method

`skip` specifies how many levels of stack to skip while getting caller
name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.
An empty string is returned if skipped levels exceed stack height

from https://gist.github.com/techtonik/2151727
"""
def caller_name(skip=3):

    parentframe = sys._getframe(skip)

    module_name_chain_list = []
    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    if module:
        module_name_chain_list.append(module.__name__)
    # detect classname
    if 'self' in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        module_name_chain_list.append(parentframe.f_locals['self'].__class__.__name__)
    codename = parentframe.f_code.co_name
    # top level usually
    if codename != '<module>':
        # function or a method
        module_name_chain_list.append(codename)
    del parentframe
    return ".".join(module_name_chain_list)
