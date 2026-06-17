import sys 
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil

library_path = "./lib" 
if library_path not in sys.path:
        sys.path.insert(0, library_path)

import nebula_cert_core as ncm_core
import nebula_cert_executor as executor
from yaml_proxy import Host

MIN_X_SIZE = 360
MIN_Y_SIZE = 710
DEFAULT_X_SIZE = 800
DEFAULT_Y_SIZE = 710
DEFAULT_X_CORD = 3000 # TODO: change this to a reasonable value
DEFAULT_Y_CORD = 250


core = ncm_core.Core()

def populate_entrybox(entrybox, text):
    entrybox.delete(0,tk.END)
    entrybox.insert(0, text)

def populate_host_listbox(listbox, hosts):
    listbox.delete(0,tk.END)
    for host in hosts:
        host_name = host.host_name
        host_ip = host.ip
        msg = None
        try:
            notes = host.note
            msg = f"- {host_name}: {notes}"
        except:
            msg = f"- {host_name}" 
                
        listbox.insert(tk.END, msg)
        listbox.insert(tk.END, f"  {host_ip}")
        listbox.insert(tk.END,"______________________")

def select_host_from_listbox(listbox):
    if not listbox.curselection(): # do nothing if no item is selected
        return None
    host_index = listbox.curselection()[0] # only delete the first selected item (selectmode should == SINGLE)
    if(host_index > 0):
        host_index = (int)(host_index/3) # because we're using 3 lines for each list item
    return host_index
    
def delete_host_from_listbox(listbox, hosts):
    host_index = select_host_from_listbox(listbox)
    if not host_index is None:
        del hosts[host_index]
        populate_host_listbox(listbox, hosts)

class App:   
    def __init__(self, root=None):
        global core

        self.nebula_cert_cmd = shutil.which("nebula-cert")
        self.executor = executor.NebulaCertExecutor(self.nebula_cert_cmd)
        self.root = root
        self.lighthouse_window = Host_Window(
            master=self.root, 
            app=self, 
            title="Lighthouse", 
            hosts=core.lighthouses)
        self.host_window = Host_Window(
            master=self.root, 
            app=self, 
            title="Host", 
            hosts=core.hosts)


        self.menubar = tk.Menu(self.root)
      
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both",expand=True)
        
        ## Certificate Section
        tk.Label(self.main_frame, text="Certificate").pack(anchor="w")
        
        cert_frame = tk.Frame(self.main_frame)
        cert_frame.pack(fill="x")

        cert_columns_frame = tk.Frame(cert_frame)
        cert_columns_frame.pack(ipady=5,fill="x")

        cert_left_frame = tk.Frame(cert_columns_frame)
        cert_left_frame.pack(padx=5, side="left")
        tk.Label(cert_left_frame, text="Domain").pack(anchor="w")
        tk.Label(cert_left_frame, text="Duration (hours)").pack(anchor="w")

        cert_right_frame = tk.Frame(cert_columns_frame)
        cert_right_frame.pack(padx=5,fill="x",expand=True,side="right")
        self.cert_domain_box = tk.Entry(cert_right_frame)
        self.cert_duration_box = tk.Entry(cert_right_frame)
        self.cert_domain_box.pack(fill="x",expand=True)
        self.cert_duration_box.pack(fill="x",expand=True)

        cert_button_frame = tk.Frame(cert_frame)
        cert_new_config_button = tk.Button(cert_button_frame, text="Save Config", command=self.save_config)
        cert_new_config_button.pack(side="left")
        cert_load_config_button = tk.Button(cert_button_frame, text="Load Config", command=self.load_config)
        cert_load_config_button.pack(side="left")
        cert_generate_button = tk.Button(cert_button_frame, text="Generate Certs", command=self.generate_certs)
        cert_generate_button.pack(side="right")
        deploy_button = tk.Button(cert_button_frame, text="Destination Folder", command=self.set_deploy_location)
        deploy_button.pack(side="right")
        cert_button_frame.pack(padx=10,fill="both",expand=True)


        ## Lighthouse Section
        lighthouse_frame = tk.Frame(self.main_frame)
        lighthouse_frame.pack(padx=10, pady=10,fill="x",expand=True)

        tk.Label(lighthouse_frame, text="Lighthouses").pack(anchor='w')
        self.lighthouse_host_listbox = tk.Listbox(lighthouse_frame, selectmode=tk.BROWSE)
        self.lighthouse_host_listbox.pack(fill="x",expand=True)

        lighthouse_host_delete_button = tk.Button(lighthouse_frame, text="Delete", command=lambda: delete_host_from_listbox(self.lighthouse_host_listbox, core.lighthouses))
        lighthouse_host_delete_button.pack(side="right")

        lighthouse_host_edit_button = tk.Button(lighthouse_frame, text="Edit", command=self.edit_lighthouse)
        lighthouse_host_edit_button.pack(side="right")

        lighthouse_host_new_button = tk.Button(lighthouse_frame, text="New", command=self.new_lighthouse)
        lighthouse_host_new_button.pack(side="left")

        ## Hosts Section
        hosts_frame = tk.Frame(self.main_frame)
        hosts_frame.pack(padx=10, pady=10,fill="both",expand=True)

        tk.Label(hosts_frame, text="Hosts").pack(anchor='w')

        hosts_listbox_frame = tk.Frame(hosts_frame)
        hosts_listbox_scrollbar = tk.Scrollbar(hosts_listbox_frame, orient="vertical")

        self.hosts_host_listbox = tk.Listbox(hosts_listbox_frame, yscrollcommand=hosts_listbox_scrollbar.set, selectmode=tk.SINGLE)
        hosts_listbox_scrollbar.config(command=self.hosts_host_listbox.yview)
        hosts_listbox_scrollbar.pack(side="right",fill="y")
        self.hosts_host_listbox.pack(fill="both",expand=True)
        hosts_listbox_frame.pack(fill="both",expand=True)

        hosts_host_delete_button = tk.Button(hosts_frame, text="Delete", command=lambda: delete_host_from_listbox(self.hosts_host_listbox,core.hosts))
        hosts_host_delete_button.pack(side="right")

        hosts_host_edit_button = tk.Button(hosts_frame, text="Edit", command=self.edit_host)
        hosts_host_edit_button.pack(side="right")

        hosts_host_new_button = tk.Button(hosts_frame, text="New", command=self.new_host)
        hosts_host_new_button.pack(side="left")

        self.populate()

        ## File Menu        
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="New", command=self.new_config)
        self.file_menu.add_command(label="Open...", command=self.load_config)
        self.file_menu.add_command(label="Save", command=self.save_config)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.root.config(menu=self.menubar)

    def populate(self):
        populate_entrybox(self.cert_domain_box, core.cert_domain)
        populate_entrybox(self.cert_duration_box, core.cert_duration)
        populate_host_listbox(self.lighthouse_host_listbox, core.lighthouses)
        populate_host_listbox(self.hosts_host_listbox, core.hosts)

    
    def main_page(self):
        self.populate()
        self.main_frame.pack(fill="both")

    def save_config(self):
        if not core.yaml_proxy.yaml_file:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".yaml",
                filetypes=[("Yaml", "*.yaml"),("Yaml", "*.yml"), ("All Files", "*.*")],
                title="Save As"
            )
            core.yaml_proxy.yaml_file = file_path

        core.cert_domain = self.cert_domain_box.get()
        core.cert_duration = ncm_core.parse_duration(self.cert_duration_box.get())

        core.write_config_to_yaml()
            
    def load_config(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".yaml",
            filetypes=[("Yaml", "*.yaml"),("Yaml", "*.yml"), ("All Files", "*.*")],
            title="Open Config"
        )
        core.open_config(file_path)
        self.populate()

    def new_config(self):
        global core 

        core = ncm_core.Core()

        self.populate()

    def exit(self):
        self.root.destroy()

    def set_deploy_location(self):
        file_path = filedialog.askdirectory(
            initialdir=self.executor.get_destination_dir(),
            title="Select Destination Directory"
        )
        if file_path:
            self.executor.set_destination_dir(file_path)
    
    def generate_certs(self):
        core.cert_domain = self.cert_domain_box.get()
        core.cert_duration = ncm_core.parse_duration(self.cert_duration_box.get())

        core.yaml_proxy.update_yaml_config(
            core.cert_domain,
            core.cert_duration,
            core.lighthouses,
            core.hosts)
        
        if self.nebula_cert_cmd is None:
            messagebox.showerror(
                "Error",
                "The 'nebula-cert' utility does not appear to be installed on this system.")
        else:
            # print(core.yaml_proxy.to_string()) # TODO: remove this
            try:
                result = self.executor.generate_certs(
                    core.cert_domain,
                    core.cert_duration,
                    core.lighthouses,
                    core.hosts)
                if result: messagebox.showinfo(
                    "Success!", 
                    f"The new certificates generated successfully here:\n\n{self.executor.get_destination_dir()}")
            except Exception as e:
                messagebox.showerror(
                    "Error", 
                    f"An error occured when generating the certificates.\n\n{e}")

    def new_lighthouse(self):
        self.main_frame.pack_forget()
        self.lighthouse_window.start_page(None)

    def new_host(self):
        self.main_frame.pack_forget()
        self.host_window.start_page(None)

    def edit_lighthouse(self):
        host_index = select_host_from_listbox(self.lighthouse_host_listbox)
        
        if not host_index is None:
            self.main_frame.pack_forget()
            self.lighthouse_window.start_page(host_index)

    def edit_host(self):
        host_index = select_host_from_listbox(self.hosts_host_listbox)
        
        if not host_index is None:
            self.main_frame.pack_forget()
            self.host_window.start_page(host_index)    

class Host_Window:
    def populate_groups_listbox(self, listbox, groups):
        listbox.delete(0,tk.END)
        for group in groups:
            listbox.insert(tk.END, group)

    def __init__(self, master=None, app=None, title=None, hosts=None, host_index=None):
        label_x_padding = 5
        label_y_padding = 3
        self.master = master
        self.app = app
        self.title_type = title
        self.window_title = tk.StringVar()
        self.is_qr_code_checked = tk.BooleanVar()
        self.window_title.set(title)
        self.main_frame = tk.Frame(self.master)
        self.hosts = hosts
        self.host_index=host_index       

        tk.Label(self.main_frame, textvariable=self.window_title).pack()

        form_frame = tk.Frame(self.main_frame)
        form_frame.pack(fill="both")

        right_column = tk.Frame(form_frame)
        right_column.pack(padx=10, side="right",fill="both",expand=True)

        left_column = tk.Frame(form_frame)
        left_column.pack(side="left", anchor="n")
        
        # Name
        tk.Label(left_column, text="Name").pack(ipadx=label_x_padding, anchor='e')
        self.name_entry_box = tk.Entry(right_column)
        self.name_entry_box.pack(fill="x",expand=True)
        
        # IP Address
        tk.Label(left_column, text="IP Address (CIDR notation)").pack(ipadx=label_x_padding, pady=label_y_padding-2, anchor='e')
        self.ip_entry_box = tk.Entry(right_column)
        self.ip_entry_box.pack(fill="x",expand=True)
  
        # Architecture
        self.arch = tk.StringVar()
        tk.Label(left_column, text="Architecture").pack(ipadx=label_x_padding, pady=label_y_padding-3, anchor='e')
        self.arch_combo_box = ttk.Combobox(right_column, textvariable=self.arch)
        self.arch_combo_box['values'] = ncm_core.NEBULA_ARCH
        self.arch_combo_box.current(0)
        self.arch_combo_box.pack(fill="x",expand=True)
        
        # Device Cert
        self.device_cert = tk.StringVar()
        tk.Label(left_column, text="Device Certificate").pack(ipadx=label_x_padding,pady=label_y_padding, anchor='e')
        device_cert_frame = tk.Frame(right_column)
        device_cert_frame.pack(fill="x",expand=True)

        self.device_cert_entry_box = tk.Entry(device_cert_frame,textvariable=self.device_cert)
        self.device_cert_entry_box.pack(side="left", fill="x",expand=True)
        device_cert_button = tk.Button(device_cert_frame, text="Select", command=self.select_certificate)
        device_cert_button.pack(side="right")
        
        # QR Code
        tk.Label(left_column, text="Generate QR code?").pack(ipadx=label_x_padding, pady=label_y_padding-3, anchor='e')
        self.qr_code_check_box = tk.Checkbutton(right_column, variable=self.is_qr_code_checked)
        self.qr_code_check_box.pack(anchor='w')
        
        # Notes
        tk.Label(left_column, text="Notes").pack(ipadx=label_x_padding, pady=label_y_padding, anchor='e')
        self.notes_entry_box = tk.Entry(right_column)
        self.notes_entry_box.pack(fill="x",expand=True)

        # Groups
        tk.Label(left_column, text="Groups").pack(ipadx=label_x_padding, pady=label_y_padding, anchor='e')
        groups_frame = tk.Frame(right_column)
        groups_frame.pack(fill="x",expand=True)

        self.groups_entry_box = tk.Entry(groups_frame)
        self.groups_entry_box.pack(side="left",fill="x",expand=True)
        groups_add_button = tk.Button(groups_frame, text="Add", width=5, command=self.add_group)
        groups_add_button.pack(side="right")

        groups_listbox_frame = tk.Frame(right_column)
        groups_listbox_frame.pack(fill="both",expand=True)
        groups_delete_button = tk.Button(groups_listbox_frame, text="Delete", width=5, command=self.delete_group)
        groups_delete_button.pack(side="right",anchor="n")
        self.groups_listbox = tk.Listbox(groups_listbox_frame)
        self.groups_listbox.pack(side="right",fill="both",expand=True)

        # Buttons
        buttons_frame = tk.Frame(self.main_frame)
        tk.Button(buttons_frame, text="Generate New Certificate", command=self.generate_host_cert).pack(side="left",anchor='w')
        tk.Button(buttons_frame, text="Save", command=lambda: self.save(hosts)).pack(side="right",anchor='e')
        tk.Button(buttons_frame, text="Cancel", command=self.cancel).pack(side="right",anchor='e')
        buttons_frame.pack(anchor='s',fill='x')

    def start_page(self,host_index):
        if host_index == None:
            self.window_title.set(f"New {self.title_type}")
        else:
            self.window_title.set(f"Edit {self.title_type}")
            self.host_index = host_index
            host = self.hosts[host_index]
            
            # name
            populate_entrybox(self.name_entry_box,host.host_name)
            
            # ip
            populate_entrybox(self.ip_entry_box,host.ip)
            
            # arch
            try:
                index = 0
                arch = host.arch
                if arch:
                    index = ncm_core.NEBULA_ARCH.index(arch)
            except:
                pass
            finally:
                self.arch_combo_box.current(index)
            
            # device cert
            self.device_cert.set(host.device_cert)

            # qr code
            self.is_qr_code_checked.set(host.make_qr_code)

            # note
            populate_entrybox(self.notes_entry_box,host.note)

            # groups
            self.populate_groups_listbox(self.groups_listbox,host.groups)

        self.main_frame.pack(fill="both")

    def add_group(self):
        self.groups_listbox.insert(tk.END,self.groups_entry_box.get())
        self.groups_entry_box.delete(0,tk.END)

    def delete_group(self):
        index = self.groups_listbox.curselection()

        if not index is None:
            self.groups_listbox.delete(index)

    def select_certificate(self):
        file_path = filedialog.askopenfile(
            defaultextension=".pub",
            filetypes=[("Public Key", "*.pub"),("All Files", "*.*")],
            title="Select Device Public Key"
        )
        if file_path:
            self.device_cert.set(file_path.name)

    def generate_host_cert(self):
        host = Host(
                f"{self.name_entry_box.get()}",
                f"{self.ip_entry_box.get()}",
                f"{self.arch_combo_box.get()}",
                list(self.groups_listbox.get(0,tk.END)),
                f"{self.notes_entry_box.get()}",
                f"{self.device_cert.get()}",
                f"{self.is_qr_code_checked.get()}"
            )

        if self.app.nebula_cert_cmd is None:
            messagebox.showerror(
                "Error",
                "The 'nebula-cert' utility does not appear to be installed on this system.")
        else:
            try:
                result = self.app.executor.sign_host(
                    host,
                    core.cert_domain)
                if result: messagebox.showinfo(
                    "Success!", 
                    f"The new certificate generated successfully here:\n\n{self.app.executor.get_destination_dir()}")
            except Exception as e:
                messagebox.showerror(
                    "Error", 
                    f"An error occured when generating the certificates. \n\n{e}")

    def save(self, hosts):
        host = Host(
                f"{self.name_entry_box.get()}",
                f"{self.ip_entry_box.get()}",
                f"{self.arch_combo_box.get()}",
                list(self.groups_listbox.get(0,tk.END)),
                f"{self.notes_entry_box.get()}",
                f"{self.device_cert.get()}",
                f"{self.is_qr_code_checked.get()}"
            )
            
        if self.host_index == None: # save new host
            hosts.append(host)
        else:                       # save edited host
            hosts[self.host_index] = host

        # clear the form
        self.host_index = None
        self.name_entry_box.delete(0,tk.END)
        self.ip_entry_box.delete(0,tk.END)
        self.device_cert.set("")
        self.arch_combo_box.current(0)
        self.notes_entry_box.delete(0,tk.END)
        self.groups_entry_box.delete(0,tk.END)
        # swap windows
        self.main_frame.pack_forget()
        self.app.main_page()

    def cancel(self):
        # clear the form
        self.host_index = None
        self.name_entry_box.delete(0,tk.END)
        self.ip_entry_box.delete(0,tk.END)
        self.device_cert.set("")
        self.arch_combo_box.current(0)
        self.notes_entry_box.delete(0,tk.END)
        self.groups_entry_box.delete(0,tk.END)
        # swap windows
        self.main_frame.pack_forget()
        self.app.main_page()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Nebula Cert Manager")
    root.minsize(MIN_X_SIZE,MIN_Y_SIZE)
    root.geometry(f"{DEFAULT_X_SIZE}x{DEFAULT_Y_SIZE}+{DEFAULT_X_CORD}+{DEFAULT_Y_CORD}")

    app = App(root)
    root.mainloop()