import r2pipe
import sys

def main():
    if len(sys.argv) < 2:
        print("[ * ] User the path of libflutter.so\n    example: ssl_flutter_killer.py ~/libflutter.so")
        sys.exit(1)
    analyse(sys.argv[1])

def create_flutter_native_hook(addr):
    print("[ + ] Creating Frida Script")
    conteudo = f"""
     /***************************************************************
        12/2024
        This script bypass native flutter ssl pinning @android
        Generated by ssl_flutter_killer
        by @brunovais
        -> https://github.com/brunovais/ssl_flutter_killer
    ***************************************************************/
    Interceptor.attach(Module.findExportByName(null, "android_dlopen_ext"), {{
    onEnter: function (args) {{
        var lib = args[0].readCString();
        if (lib && lib.includes("libflutter.so")) {{
            this.hook = true;
        }}
    }},
    onLeave: function (retval) {{
        if (this.hook) {{
            var module = Module.findBaseAddress("libflutter.so");
            if (module) {{
                //
                var targetAddress = module.add(0x{addr});
                Interceptor.attach(targetAddress, {{
                    onLeave: function (ret) {{
                        console.log("[ + ] Flutter SSL Cert Chain");
                        ret.replace(0x1);
                    }}
                }});
            }} else {{
                console.error("[ - ] Módulo libflutter.so não encontrado!");
            }}
        }}
    }}
}});"""
    with open("ssl_flutter_unpinning.js", "w") as file:
        file.write(conteudo)
        print("[ :D ] ssl_flutter_unpinning.js Created!")

def analyse(path):
    r2 = r2pipe.open(path)
    r2.cmd("aaa")
    strings = r2.cmdj("izzj")

    for string in strings:
        if "ssl_server" in string['string']:
            print(f"[ + ] ssl_server string addres: {hex(string['vaddr'])}")
            r2.cmd(f"s {hex(string['vaddr'])}")
            string_function = r2.cmd("pd 1")
            function_address = string_function.split("fcn.")[1].split(" @")[0]
            print(f"[ + ] address of target function found @ {function_address}")
            create_flutter_native_hook(function_address)
    r2.quit()

if __name__ == "__main__":
    main()