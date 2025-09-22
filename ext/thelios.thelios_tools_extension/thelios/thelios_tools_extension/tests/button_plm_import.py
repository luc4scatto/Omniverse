print("[thelios.thelios_tools_extension] Extension startup")

        self._count = 0
        self._window = ui.Window(
            "Thelios Tools", width=800, height=300
        )
        with self._window.frame:
            with ui.VStack(spacing=5):
                # Prima riga: 3 ComboBox, 1 CheckBox e 1 Button allineati orizzontalmente
                with ui.HStack(height=30, spacing=20):
                    
                    model = ui.SimpleIntModel(262)
                    
                    self.release_field = ui.IntField(model)
                    self.brand_combo = ui.ComboBox(0, *combo_elements).model
                    self.type_combo = ui.ComboBox(0, *genres).model
                    button1 = ui.Button("Esegui")
                    
                # Seconda riga: 1 LineEdit, 2 ComboBox e 1 Button allineati orizzontalmente
                with ui.HStack(height=30, spacing=10):
                    line_edit = ui.StringField()
                    #combo4 = ui.ComboBox(0, ["Valore 1", "Valore 2", "Valore 3"])
                    #combo5 = ui.ComboBox(0, ["Item A", "Item B", "Item C"])
                    button2 = ui.Button("Conferma")
                    
                # Funzioni di callback
                def on_button1_clicked():
                    index_brand = self.brand_combo.get_item_value_model().get_value_as_int()
                    index_type = self.type_combo.get_item_value_model().get_value_as_int()
                    
                    season_value = model.get_value_as_int()
                    brand_value = str(combo_elements[index_brand])
                    type_value = str(genres[index_type])
                    
                    if type_value == "All Woman":
                        res_query_optical_woman = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),"Optical - Woman")
                        res_query_sun_woman = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),"Sun - Woman")
                        
                        res_query_sun = list(set(res_query_optical_woman).union(set(res_query_sun_woman)))
                        sorted_list = sorted(res_query_sun, key=lambda x: x[0])
                        print(sorted_list)
                        
                    elif type_value == "All Man":
                        res_query_optical_man = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),"Optical - Man")
                        res_query_sun_man = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),"Sun - Man")
                        
                        result_query_man = list(set(res_query_optical_man).union(set(res_query_sun_man)))
                        sorted_list = sorted(result_query_man, key=lambda x: x[0])
                        print(sorted_list)
                        
                    else:
                        res_query = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),str(type_value))
                        print(res_query)
                    
                def on_button2_clicked():
                    print("Pulsante 'Conferma' premuto")
                    print(f"Testo inserito: {line_edit.model.get_value()}")
                    
                # Assegno i callback ai pulsanti
                button1.set_clicked_fn(on_button1_clicked)
                button2.set_clicked_fn(on_button2_clicked)