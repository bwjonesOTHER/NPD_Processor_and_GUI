with open('standalone/app.py', 'r') as f:
    content = f.read()

old_except = """        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": str(e)}), 500"""

new_except = """        except Exception as e:
            import traceback
            traceback.print_exc()
            with open("debug_log.txt", "a") as f_dbg:
                f_dbg.write(f"EXCEPTION in generate_plots: {e}\\n")
                f_dbg.write(traceback.format_exc() + "\\n")
            return jsonify({"success": False, "error": str(e)}), 500"""

content = content.replace(old_except, new_except)

with open('standalone/app.py', 'w') as f:
    f.write(content)
