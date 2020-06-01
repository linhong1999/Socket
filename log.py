# # # coding=utf8
# # import sys
# # import traceback
# # import win32con
# # import win32evtlog
# # import win32evtlogutil
# # import winerror
# #
# # try:
# #     from _utils.patrol2 import run_cmd, data_format, report_format
# # except:
# #     print
# #     'no module _utils'
# # import platform
# # import datetime, psutil
# #
# #
# # def getAllEvents(server, logtypes, time_flag):
# #     """
# #     """
# #     if not server:
# #         serverName = "localhost"
# #     else:
# #         serverName = server
# #     for logtype in logtypes:
# #         result = getEventLogs(server, logtype, time_flag)
# #         return result
# #
# #
# # # ----------------------------------------------------------------------
# # def getEventLogs(server, logtype, time_flag, logPath=None):
# #     """
# #     Get the event logs from the specified machine according to the
# #     logtype (Example: Application) and save it to the appropriately
# #     named log file
# #     """
# #     print("Logging %s events" % logtype)
# #
# #     # log = codecs.open(logPath, encoding='utf-8', mode='w')
# #     # line_break = '-' * 80
# #     #
# #     # log.write("\n%s Log of %s Events\n" % (server, logtype))
# #     # log.write("Created: %s\n\n" % time.ctime())
# #     # log.write("\n" + line_break + "\n")
# #     # 读取本机的,system系统日志
# #     hand = win32evtlog.OpenEventLog(server, logtype)
# #     # 获取system日志的总行数
# #     total = win32evtlog.GetNumberOfEventLogRecords(hand)
# #     print("Total events in %s = %s" % (logtype, total))
# #
# #     flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
# #     events = win32evtlog.ReadEventLog(hand, flags, 0)
# #     # 错误级别类型
# #     evt_dict = {win32con.EVENTLOG_AUDIT_FAILURE: 'EVENTLOG_AUDIT_FAILURE',
# #                 win32con.EVENTLOG_AUDIT_SUCCESS: 'EVENTLOG_AUDIT_SUCCESS',
# #                 win32con.EVENTLOG_INFORMATION_TYPE: 'EVENTLOG_INFORMATION_TYPE',
# #                 win32con.EVENTLOG_WARNING_TYPE: 'EVENTLOG_WARNING_TYPE',
# #                 win32con.EVENTLOG_ERROR_TYPE: 'EVENTLOG_ERROR_TYPE'}
# #
# #     try:
# #         events = 1
# #         count = 0
# #         while events:
# #             events = win32evtlog.ReadEventLog(hand, flags, 0)
# #
# #             for ev_obj in events:
# #                 the_time = ev_obj.TimeGenerated.Format()  # '12/23/99 15:54:09'
# #                 the_time = datetime.datetime.strptime(the_time, "%m/%d/%y %H:%M:%S")
# #                 if the_time < time_flag:
# #                     continue
# #                 evt_id = str(winerror.HRESULT_CODE(ev_obj.EventID))
# #                 computer = str(ev_obj.ComputerName)
# #                 cat = ev_obj.EventCategory
# #                 ##        seconds=date2sec(the_time)
# #                 record = ev_obj.RecordNumber
# #                 msg = win32evtlogutil.SafeFormatMessage(ev_obj, logtype)
# #
# #                 source = str(ev_obj.SourceName)
# #                 if not ev_obj.EventType in evt_dict.keys():
# #                     evt_type = "unknown"
# #                 else:
# #                     evt_type = str(evt_dict[ev_obj.EventType])
# #
# #                 if evt_id == '4625':
# #                     count += 1
# #                     # log.write("Event Date/Time: %s\n" % the_time)
# #                     # log.write("Event ID / Type: %s / %s\n" % (evt_id, evt_type))
# #                     # log.write("Record #%s\n" % record)
# #                     # log.write("Source: %s\n\n" % source)
# #                     # log.write(msg)
# #                     # log.write("\n\n")
# #                     # log.write(line_break)
# #                     # log.write("\n\n")
# #         return count
# #     except:
# #         print(traceback.print_exc(sys.exc_info()))
# #
# #         sys.exit(1)
# #
# #
# # def get_start_time():
# #     dt = datetime.datetime.fromtimestamp(psutil.boot_time())
# #     return dt
# #
# #
# # if __name__ == "__main__":
# #     time_flag = get_start_time()
# #     print(time_flag)
# #
# #     server = None  # None = local machine
# #     logTypes = ["Security"]  # "System", "Application",
# #     result = getAllEvents(server, logTypes, time_flag)
# #     if result == 0:
# #         alert = 0
# #     else:
# #         alert = 1
# #
# #     hostname = platform.node()
# #     report = data_format('登录失败次数', result, alert)
# #     reports = report_format(hostname, report, is_json=True)
# #
# #     print(reports)
# import mmap
# import contextlib
#
# from Evtx.Evtx import FileHeader
# from Evtx.Views import evtx_file_xml_view
# from xml.dom import minidom
#
# def MyFun():
#     EvtxPath = "D:Application.evtx"
#
#     with open(EvtxPath,'r') as f:
#         with contextlib.closing(mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)) as buf:
#             fh = FileHeader(buf,0)
#             for xml, record in evtx_file_xml_view(fh):
#                 #只输出事件ID为4624的内容
#                 InterestEvent(xml,4624)
#             print()
#
# # 过滤掉不需要的事件，输出感兴趣的事件
# def InterestEvent(xml,EventID):
#     xmldoc = minidom.parseString(xml)
#     # 获取EventID节点的事件ID
#     booknode=root.getElementsByTagName('event')
#     for booklist in booknode:
#         bookdict={}
#         bookdict['id']=booklist.getAttribute('id')
#         bookdict['head']=booklist.getElementsByTagName('head')[0].childNodes[0].nodeValue.strip()
#         bookdict['name']=booklist.getElementsByTagName('name')[0].childNodes[0].nodeValue.strip()
#         bookdict['number']=booklist.getElementsByTagName('number')[0].childNodes[0].nodeValue.strip()
#         bookdict['page']=booklist.getElementsByTagName('page')[0].childNodes[0].nodeValue.strip()
#     if EventID == eventID:
#         print(xml)
#
# if __name__ == '__main__':
#     MyFun()
#
