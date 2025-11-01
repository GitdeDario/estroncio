#*********************************************************************************************
#		DEFINO CONSTANTES y VARIABLES
#**********************************************************************************************
# Definición de constantes usadas en el LCD
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Constantes de tiempo usadas en el LCD
E_PULSE = 0.0005
E_DELAY = 0.0005

#Otras constantes
TIEMPO_ANTIRREBOTES = 0.020	#20ms para la funcionr "no_rebote"
TIEMPO_REFRESCO_LCD = 1		#1 segundo para que recargar datos de la pista que se está reproduciendo
TIEMPO_ESPERA_ENCODER = 10	# Espera antes de salir del loop de esperar a que se actue sobre el encoder o se de enter en el encoder
#Variables para la máquina de estado
Ei = Er1 = Er2 = Erf = Ei1 = Ei2 = Eif = False	#Estados para la máquina de estados del encoder
FINErf = FINEif = True

# Motor PAP/stepper
# Secuencia de paso media. Menos par y menos consumo; movimientos más suaves
StepCount = 8
Seq = []
Seq = [i for i in range(0, StepCount)]
Seq[0] = [1,0,0,0]
Seq[1] = [1,1,0,0]
Seq[2] = [0,1,0,0]
Seq[3] = [0,1,1,0]
Seq[4] = [0,0,1,0]
Seq[5] = [0,0,1,1]
Seq[6] = [0,0,0,1]
Seq[7] = [1,0,0,1]




#***********************************************************************************************
#	DEFINO VARIABLES PARA LA MÁQINA DE ESTADOS
#************************************************************************************************

#SI SE AGREGAN FUNCIONES, PONERLAS EN EL FINAL DE ESTA LISTA PARA ASÍ NO AFECTAR EL FUNCIONAMIENTO QUE SE TIENE HASTA EL MOMENTO.
estado = ["play", "prev", "next", "stop", "volume +10", "volume -10", "random", "pause", "off"]
indice_temp = 3
indice = 3	# 3 = "stop"
FLAG_primera_entrada = True
flag_actualizar_lcd = False
no_estaba_seteado_el_stop = True
no_estaba_seteado_el_pause = True