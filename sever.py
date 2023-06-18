import json
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep
import io
import sys
import datetime

# 定义 HTTP 请求处理类
class RequestHandler(BaseHTTPRequestHandler):
    # 设置 HTTP 响应头
    def _set_response(self, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    # 处理 GET 请求
    def do_GET(self):
        # 如果请求根路径，则返回 index.html 文件
        if self.path == '/':
            self.path = 'index.html'
        try:
            sendReply = False
            if self.path.endswith(".html"):
                mimetype = 'text/html'
                sendReply = True
            elif self.path.endswith(".css"):
                mimetype = 'text/css'
                sendReply = True
            elif self.path.endswith(".js"):
                mimetype = 'application/javascript'
                sendReply = True
            if sendReply == True:
                with open(curdir + sep + self.path, 'rb') as f:
                    self._set_response(content_type=mimetype)
                    self.wfile.write(f.read())
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    # 处理 POST 请求
    def do_POST(self):
        
        # 获取请求体中的 JSON 数据
        content_length = int(self.headers['Content-Length'])
        json_str = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(json_str)

        # 从 JSON 数据中获取 Python 代码并执行
        python_code = data.get('python_code', '')
        print(f"输入的代码：{python_code}")
        result_buf = io.StringIO()
        sys.stdout = result_buf
        try:
            if 'exit()' in python_code:
                pass
            elif 'input()' in python_code:
                pass
            elif 'os.' in python_code:
                pass
            else:
                # 用 exec 运行多行代码
                exec(python_code)
                result = ''
        except Exception as e:
            # 如果执行出错，则返回异常信息
            result = str(e)
        finally:
            sys.stdout = sys.__stdout__
            print(result_buf.getvalue())

        # 判断输入内容是否包含 print 函数，如果包含，则返回 print_result，否则返回 result
        if 'print(' in python_code:
            result = result_buf.getvalue()
        else:
            result = str(result_buf.getvalue())

        # 判断执行结果是否超过 100 行
        result_lines = result.splitlines()

        if len(result_lines) > 100:
            # 超过 100 行则只显示前 100 行，并在最后一行添加 "......"
            result_lines = result_lines[:100]
            result_lines.append('......输出过多')
            result = '\r\n'.join(result_lines)
        
        else:
            result = result

        print(f"执行结果：{result}")
        ip = self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or self.client_address[0]
        print(f"用户ip是{ip}")
        # 将输入输出保存到文件中
        timestamp = datetime.datetime.now().strftime('%Y年%m月%d日_%H时%M分%S秒')
        with open('web.txt', 'a') as f:
            
            
            f.write(f'执行时间：{timestamp}\n')
            f.write(f'输入的代码：{python_code}\n')
            f.write(f'执行结果：{result}\n')
           
            f.write(f'用户ip:{ip}\n\n')
            f.close()
            print("写入成功")
        if 'exit()' in python_code:
            response = json.dumps({'result': '禁止使用'})
        elif 'input()' in python_code:
            response = json.dumps({'result': '禁止使用'})
        elif 'os.' in python_code:
            response = json.dumps({'result': '禁止使用'})
        else:
            response = json.dumps({'result': result})

        self._set_response(content_type='application/json')
        self.wfile.write(response.encode('utf-8'))


# 启动 HTTP 服务器
def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Server listening on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()