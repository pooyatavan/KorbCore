

def FlaskSetup():
    @app.route("/", methods=['GET', 'POST'])
    @app.route('/setup', methods=['GET', 'POST'])
    def setup():
        form = SetupForm()
        if form.validate_on_submit():
            cmsservername = form.CMSServerName.data
            cmsserverip = form.CMSServerIP.data
            cmsport = form.CMSPort.data

            sqlip = form.SQLServerIP.data
            sqlport = form.SQLServerPORT.data
            sqlusername = form.SQLUsername.data
            sqlpassword = form.SQLPaswword.data

            coresqlip = form.CoreSQLServerIP.data
            coresqlport = form.CoreSQLServerPORT.data
            coresqlusername = form.CoreSQLUsername.data
            coresqlpassword = form.CoreSQLPaswword.data
            if cmsservername or cmsserverip or cmsport or sqlip or sqlport or sqlusername or sqlpassword or coresqlip or coresqlport or coresqlusername or coresqlpassword == "":
                flash(MSGList.EmptyFields.value, "alert-warning")
            else:
                ips = [cmsserverip, sqlip, coresqlip]
                for ip in ips:
                    if IpFormatCheck(ip) == True:
                        Config.write('core', 'servername', cmsservername)
                        Config.write('core', 'ip', cmsserverip)
                        Config.write('core', 'port', cmsport)
                        Config.write('core', 'setup', 'disable')
                        restart()
                    else:
                        flash(MSGList.WrongIPAddressFormat.value, "alert-error")
        return render_template('setup.html', form=form)
    


        @app.errorhandler(404)
    def page_not_found(e):
        return redirect(url_for('messa'))
    app.register_error_handler(404, page_not_found)

    @app.errorhandler(403)
    def page_not_found(e):
        return redirect(url_for('setup'))
    app.register_error_handler(403, page_not_found)

    @app.errorhandler(500)
    def page_not_found(e):
        return redirect(url_for('setup'))
    app.register_error_handler(500, page_not_found)