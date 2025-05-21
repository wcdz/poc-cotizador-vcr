PROBABILIDAD_VIVOS = 1 # AB2 [CONSTANTE]

'''
AB (Vivos Inicio): (Inicio) AF2 => AD2 - AE2
    
    AD (Vivo Inicio - Fallecidos): AB2 - AC2
        AB2 = PROBABILIDAD_VIVOS [CONSTANTE]
        AC2 = AB2 * Z2 / 1000

            Z (Mortalidad qx o/oo mult x cada frecuencia) = X2 * H2 
                X (Mortalidad qx o/oo x cada frecuencia) = V2 * ( 1 - POTENCIA( 1-F2/1000; 1/ ( 12/Parametros_Supuestos!$C$17)))*1000
                
                    V (Validador de Pago de primas) = SI((B2-1)/Parametros_Supuestos!$C$17=ENTERO((B2-1)/Parametros_Supuestos!$C$17);1;0)
                        B2 = PROBABILIDAD_VIVOS [CONSTANTE]
                        C17 = cantidad_meses_frecuencia [CALCULAR EN BASE A frecuencia_pago_primas]
                    
                    F (Mortalidad qx o/oo Anual) = =+SI(C2>Parametros_Supuestos!$C$19;0;SI(Y(Parametros_Supuestos!$C$14="No Fuma";Parametros_Supuestos!$C$13="M");BUSCARV('Expuestos Mes'!C2;TM!$B$8:$D$87;2;0); SI(Y(Parametros_Supuestos!$C$14="No Fuma";Parametros_Supuestos!$C$13="F");BUSCARV('Expuestos Mes'!C2;TM!$B$8:$D$87;3;0);SI(Y(Parametros_Supuestos!$C$14="Fuma";Parametros_Supuestos!$C$13="M");BUSCARV('Expuestos Mes'!C2;TM!$B$8:$F$87;4;0);BUSCARV('Expuestos Mes'!C2;TM!$B$8:$F$87;5;0)))))
                    
                        C2 = +Parametros_Supuestos!$C$15+(A2-1)
                            C15 = edad_actuarial [INPUT]
                            A (Año Poliza) = [INPUT] [1 - 70] [SE EMPIEZA EN 1]
                        
                        C19 = duracion_pagos [CALCULAR periodo_vigencia + edad_contratacion - 1]
                        
                        C14 = Condicion_fuma [INPUT] = No fuma
                        
                        C13 = sexo [INPUT] = M || F
                        
                        C2 = +Parametros_Supuestos!$C$15+(A2-1)
                        
                        TM (Tabla Mortalidad) = return Hombres No fuma _ value || Mujeres No fuma _ value || Hombres Fuma _ value || Mujeres Fuma _ value
                    
                    C17 = cantidad_meses_frecuencia [CALCULAR EN BASE A frecuencia_pago_primas]
                
                H (Mortalidad Ajuste) = +Parametros_Supuestos!$C$63 (Expuestos (tarifa de reaseguro)) [INPUT]
        
    AE (Caducados): AD2 * W2

        AD (Vivos Inicio - Fallecidos): AB2 - AC2 [YA ESTA ANALIZADO]
        
        W2 (% Caducidad x cada frecuencia): EN DURO ASSETS [CONSULTAR PORQUE NO LO USA]
        

AF (Vivos Final): 
        AF2 => AD2 - AE2 [YA ESTA ANALIZADO]

-------------------------------------------------------------------

M (Fallecidos) => L2 * J2 / 1000

    L (Vivos Inicio): +P2
        P (Vivos Final) : N2 - O2
            
            N2 (Vivo Inicio - Fallecidos): L2 - M2
            
                L2 (Vivos Inicio): +P2 (YA ESTA ANALIZADO)
                M2 (Fallecidos): (ES LO MISMO)
            
    J (Mortalidad qx o/oo mult Mensual) => G2 * H2
        G (Mortalidad qx o/oo Mensual) => =(1-POTENCIA(1-F2/1000;1/12))*1000
            F (Mortalidad qx o/oo Anual) => =+SI(C2>Parametros_Supuestos!$C$19;0;SI(Y(Parametros_Supuestos!$C$14="No Fuma";Parametros_Supuestos!$C$13="M");BUSCARV('Expuestos Mes'!C2;TM!$B$8:$D$87;2;0); SI(Y(Parametros_Supuestos!$C$14="No Fuma";Parametros_Supuestos!$C$13="F");BUSCARV('Expuestos Mes'!C2;TM!$B$8:$D$87;3;0);SI(Y(Parametros_Supuestos!$C$14="Fuma";Parametros_Supuestos!$C$13="M");BUSCARV('Expuestos Mes'!C2;TM!$B$8:$F$87;4;0);BUSCARV('Expuestos Mes'!C2;TM!$B$8:$F$87;5;0)))))
        
        
        H (Mortalidad Ajuste) Expuestos (tarifa de reaseguro) [INPUT] [CONSULTAR]

'''