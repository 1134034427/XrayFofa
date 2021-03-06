# -*- encoding:utf-8 -*-
import threading
import time
import os,sys
import Module.fofa
import yaml
import Module.fofareptile
import platform
import random
class scan(threading.Thread):
	def __init__(self,thread):
		threading.Thread.__init__(self)
		self.thread = thread

		#调用scan_config里面的配置

		scan_config = yaml.full_load(open('scan_config.yaml','rb'))
		self.domain_scan = scan_config['global']['scan_domain_name']
		self.reptile = scan_config['global']['fofareptile']
		if self.reptile:
			self.fofacookie = scan_config['fofa']['Fofa_Cookie']

		#[xray]

		self.file_path = scan_config['xray']['file_path']
		self.xray_file_path = scan_config['xray']['xray_file_path']
		self.input_file_type = scan_config['xray']['input_file_type']
		if self.xray_file_path == None:
			if platform.system()=="Windows": # 判断操作系统
				self.xray_file_path = 'xray_windows_amd64.exe'
			else:
				self.xray_file_path = './xray_linux_amd64'
		if self.input_file_type == None:
			self.input_file_type = 'html'
		if self.file_path == None:
			self.file_path ='./'+self.input_file_type
		if not os.path.exists(self.input_file_type):
			os.makedirs(self.input_file_type)

		#[fofa]
		
		self.fofa_email = scan_config['fofa']['Fofa_email']
		self.fofa_key = scan_config['fofa']['Fofa_key']
		self.syntax = scan_config['fofa']['fofaQuerysyntax']
		if self.fofa_email == None or self.fofa_key == None:
			print('error: fofa_email 或者 fofa_key 没有输入')
			sys.exit()

	def xray(self,url):
		#xray配置
		if self.input_file_type  == 'text':
			file_path = self.file_path+"/"+str(int(time.time()))+'.txt'
		else:
			file_path = self.file_path+"/"+str(int(time.time()))+'.'+self.input_file_type
		os.system('%s webscan  --plugins phantasm,brute_force,sqldet,cmd_injection --basic-crawler %s --%s-output %s'%(self.xray_file_path,url,self.input_file_type,file_path))
	def Fofa(self,count=None): 
		#fofa扫描
		syntax=''
		if self.reptile:
			for value in self.syntax:
				syntax+=value+','
			domain = Module.fofareptile.fofascan(self.fofacookie,syntax)
			return domain
		else:
			urllist=[]
			value = ''
			for key in self.syntax:
				value+=key+','
			email = self.fofa_email
			key = self.fofa_key
			search = Module.fofa.FofaAPI(email, key)
			try:
				for host in search.get_data('%s'%(value),count, "host")['results']:
					if self.domain_scan:
						if self.getdomain(host)!=None:
							urllist.append(self.getdomain(host))
					else:
						urllist.append(self.geturl(host))
			except:
				print("KeyError:fofa连接失败,请检查email和key是否正确或者更新key!")
				sys.exit()
			return urllist
			
	def geturl(self,value): #优化url
		value =value.strip()
		if value[:4] == 'http':
			url=value
		else:
			url='http://'+value
		return url
	def getdomain(self,value): #过滤出域名
		url = value.strip()
		if url[:7] == 'http://' or url[:8] == 'https://':
			urls = url[url.index('//')+2:]
			if ':' in urls:
				urls  = urls[:urls.index(':')]
			value = urls.replace('.','')
			try:
				int(value)
			except:
				return url
	def run(self):
		#运行xray和fofa
		if self.reptile:
			while True:
				urllist = self.Fofa()
				for url in urllist:
					if self.domain_scan:
						if self.getdomain(url)==None:continue
						else:url = self.getdomain(url)
					else:url = self.geturl(url)
					self.xray(url)
		else:
			count=1
			while count<=1000:
				count+=self.thread
				urllist = self.Fofa(count)
				for url in urllist:
					self.xray(url)

if __name__=='__main__':
	print("""
\033[1;36m
___   ___ .______          ___   ____    ____  _______   ______    _______    ___      
\  \ /  / |   _  \        /   \  \   \  /   / |   ____| /  __  \  |   ____|  /   \     
 \  V  /  |  |_)  |      /  ^  \  \   \/   /  |  |__   |  |  |  | |  |__    /  ^  \    
  >   <   |      /      /  /_\  \  \_    _/   |   __|  |  |  |  | |   __|  /  /_\  \   
 /  .  \  |  |\  \----./  _____  \   |  |     |  |     |  `--'  | |  |    /  _____  \  
/__/ \__\ | _| `._____/__/     \__\  |__|     |__|      \______/  |__|   /__/     \__\ 
\033[0m
""")
	threads=[]
	global keyslist
	keyslist=[]
	scan_config = yaml.full_load(open('scan_config.yaml','rb'))
	thread_count =scan_config['global']['threads']
	for i in range(1,thread_count+1):
		threads.append(scan(i))
	for thread in threads:
		thread.start()
	for thread in threads:
		thread.join()
