"""Script temporal para generar el PDF de la clínica médica."""
from fpdf import FPDF

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_ITALIC = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Oblique.ttf"


class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "B", 12)
        self.set_fill_color(41, 128, 185)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "Clínica MediSalud — Documentación Interna", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("DejaVu", "B", 13)
        self.set_fill_color(235, 245, 255)
        self.cell(0, 10, title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        self.set_font("DejaVu", size=10)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def subsection(self, title):
        self.set_font("DejaVu", "B", 11)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")


pdf = PDF()
pdf.add_font("DejaVu", "", FONT_REGULAR)
pdf.add_font("DejaVu", "B", FONT_BOLD)
pdf.add_font("DejaVu", "I", FONT_ITALIC)
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# ─── SECCIÓN 1: POLÍTICA DE PRIVACIDAD ───────────────────────────────────────
pdf.section_title("1. Política de Privacidad de Datos del Paciente")

pdf.body_text(
    "Clínica MediSalud se compromete a proteger la privacidad y confidencialidad de los datos "
    "personales y médicos de todos sus pacientes, en estricto cumplimiento de la Ley 19.628 sobre "
    "Protección de la Vida Privada y la normativa vigente de salud en Chile."
)

pdf.subsection("1.1 Datos recopilados")
pdf.body_text(
    "La clínica recopila los siguientes datos: nombre completo, RUT, fecha de nacimiento, domicilio, "
    "teléfono de contacto, correo electrónico, ficha médica (diagnósticos, tratamientos, exámenes), "
    "información de cobertura de salud (ISAPRE o FONASA) y antecedentes familiares relevantes."
)

pdf.subsection("1.2 Finalidad del tratamiento de datos")
pdf.body_text(
    "Los datos se utilizan exclusivamente para: (a) prestar atención médica de calidad, "
    "(b) coordinar derivaciones a especialistas, (c) enviar recordatorios de citas, "
    "(d) gestionar cobros y seguros de salud, y (e) cumplir obligaciones legales. "
    "Los datos NO serán vendidos ni compartidos con terceros sin consentimiento explícito del paciente, "
    "salvo requerimiento legal o emergencia médica."
)

pdf.subsection("1.3 Derechos del paciente")
pdf.body_text(
    "Cada paciente tiene derecho a: acceder a su ficha médica en cualquier momento, solicitar "
    "corrección de datos incorrectos, pedir la eliminación de datos no necesarios para la atención "
    "(salvo obligación legal de retención), y revocar el consentimiento de uso de datos para "
    "comunicaciones no esenciales. Para ejercer estos derechos, contactar a privacidad@medisalud.cl "
    "o presencialmente en recepción."
)

pdf.subsection("1.4 Retención de datos")
pdf.body_text(
    "Las fichas médicas se conservan por un mínimo de 15 años desde la última atención, "
    "según la normativa del Ministerio de Salud de Chile. Los datos de contacto pueden eliminarse "
    "a solicitud del paciente una vez finalizada la relación con la clínica, siempre que no existan "
    "obligaciones legales pendientes."
)

pdf.subsection("1.5 Seguridad de la información")
pdf.body_text(
    "MediSalud implementa medidas de seguridad técnicas y organizacionales: cifrado de datos en "
    "tránsito y en reposo, control de acceso basado en roles (solo el equipo médico tratante puede "
    "acceder a la ficha), auditorías periódicas de acceso, y capacitación continua del personal "
    "en manejo confidencial de información."
)

# ─── SECCIÓN 2: FAQ DE TURNOS ────────────────────────────────────────────────
pdf.add_page()
pdf.section_title("2. Preguntas Frecuentes sobre Consultas y Turnos")

pdf.subsection("¿Cómo puedo agendar un turno?")
pdf.body_text(
    "Puede agendar su turno por tres vías: (1) Llamando al +56 2 2345 6789 de lunes a viernes "
    "de 8:00 a 20:00 y sábados de 9:00 a 14:00. (2) A través del portal web en www.medisalud.cl/turnos, "
    "disponible las 24 horas. (3) Presencialmente en recepción durante el horario de atención. "
    "Para pacientes nuevos, recomendamos llamar para orientación sobre el especialista adecuado."
)

pdf.subsection("¿Qué debo traer a mi primera consulta?")
pdf.body_text(
    "Para la primera consulta debe traer: cédula de identidad o pasaporte vigente, credencial "
    "de ISAPRE o carnet de FONASA, orden médica si es derivado por otro médico, exámenes "
    "o imágenes previas relacionadas con su motivo de consulta, y lista de medicamentos que "
    "toma actualmente (nombre, dosis y frecuencia)."
)

pdf.subsection("¿Con cuánta anticipación debo llegar?")
pdf.body_text(
    "Se recomienda llegar 15 minutos antes de su hora para pacientes con cita previa. "
    "Para pacientes nuevos, llegar 30 minutos antes para completar el registro. "
    "Si llega con más de 10 minutos de retraso, la clínica no puede garantizar su atención "
    "en el horario pactado y podría ser reagendado según disponibilidad del médico."
)

pdf.subsection("¿Cuánto dura una consulta?")
pdf.body_text(
    "La duración varía según especialidad: medicina general (20 minutos), especialidades "
    "como cardiología, neurología y traumatología (30 minutos), psiquiatría y psicología "
    "(45-50 minutos), y controles de seguimiento (15 minutos). Si necesita más tiempo, "
    "indíquelo al momento de agendar para reservar el bloque adecuado."
)

pdf.subsection("¿Puedo agendar para un menor de edad?")
pdf.body_text(
    "Sí. Los menores de 18 años deben estar acompañados por su padre, madre o tutor legal "
    "con documentos que acrediten la relación. Para menores de 14 años es obligatorio que "
    "el adulto esté presente durante toda la consulta. Entre 14 y 17 años, el médico puede "
    "evaluar casos donde el adolescente prefiera privacidad para ciertos temas de salud."
)

pdf.subsection("¿Se atiende sin cita previa?")
pdf.body_text(
    "Disponemos de atención de urgencias sin cita previa las 24 horas en nuestra Unidad de "
    "Urgencias. Para consultas de especialidad, se requiere cita previa. Medicina general "
    "ofrece cupos de 'atención inmediata' de lunes a viernes de 8:00 a 10:00 (orden de llegada, "
    "cupos limitados a 8 por día). Consulte disponibilidad en recepción o por teléfono."
)

# ─── SECCIÓN 3: POLÍTICA DE CANCELACIONES ────────────────────────────────────
pdf.add_page()
pdf.section_title("3. Política de Cancelaciones y Reagendamiento")

pdf.subsection("3.1 Cancelación sin costo")
pdf.body_text(
    "El paciente puede cancelar o reagendar su turno sin costo ni penalidad si lo hace con "
    "al menos 24 horas de anticipación antes del horario de la consulta. La cancelación puede "
    "realizarse por teléfono, portal web, o presencialmente. Se emitirá un comprobante de "
    "cancelación que puede usarse para reagendar sin perder prioridad."
)

pdf.subsection("3.2 Cancelación tardía (menos de 24 horas)")
pdf.body_text(
    "Si la cancelación se realiza con menos de 24 horas de anticipación, se aplicará un cargo "
    "administrativo de $5.000 CLP para pacientes particulares. Para pacientes con FONASA e ISAPRE, "
    "este cargo queda a criterio de cada convenio. En casos de fuerza mayor debidamente documentados "
    "(hospitalización, accidente), el cargo puede ser eximido previa evaluación en administración."
)

pdf.subsection("3.3 No presentación (inasistencia sin aviso)")
pdf.body_text(
    "La inasistencia sin aviso previo implica: pérdida del turno sin reembolso si se "
    "pagó con anticipación, cargo de $10.000 CLP para pacientes que reservaron sin pago previo, "
    "y anotación en la ficha del paciente. Tres inasistencias injustificadas en el año pueden "
    "resultar en restricción para agendar con ciertos especialistas de alta demanda."
)

pdf.subsection("3.4 Cancelación por parte de la clínica")
pdf.body_text(
    "En caso de que la clínica deba cancelar una cita (emergencia del médico, fuerza mayor), "
    "se notificará al paciente con al menos 2 horas de anticipación por teléfono y correo. "
    "El paciente tendrá prioridad absoluta para reagendar sin costo adicional, o recibirá "
    "reembolso total si ya había pagado. En situaciones de urgencia del médico el mismo día, "
    "se intentará derivar al paciente con otro profesional disponible."
)

pdf.subsection("3.5 Reagendamiento")
pdf.body_text(
    "Para reagendar, el paciente puede elegir cualquier horario disponible dentro de los próximos "
    "30 días sin costo adicional si cumple el plazo de 24 horas. El reagendamiento puede hacerse "
    "por los mismos canales que el agendamiento (teléfono, web, presencial). Se permite un máximo "
    "de dos reagendamientos por consulta; la tercera vez requerirá nueva solicitud de turno."
)

# ─── SECCIÓN 4: COBERTURAS MÉDICAS ───────────────────────────────────────────
pdf.add_page()
pdf.section_title("4. Guía de Convenios y Coberturas Médicas")

pdf.subsection("4.1 FONASA")
pdf.body_text(
    "MediSalud es prestador preferente de FONASA en las modalidades de Libre Elección (MLE) "
    "para todos los tramos. Los pacientes con FONASA pueden atenderse presentando su carnet "
    "vigente. La bonificación varía según tramo: Tramo A y B reciben bonificación del 100% en "
    "consultas de medicina general y hasta 80% en especialidades. Tramos C y D tienen copago "
    "según el arancel FONASA vigente. Los exámenes de laboratorio tienen bonificación del 75% "
    "en promedio para todos los tramos."
)

pdf.subsection("4.2 ISAPRE — Convenios vigentes")
pdf.body_text(
    "Tenemos convenio directo (sin desembolso anticipado) con: Banmédica, Colmena, Cruz Blanca, "
    "Consalud, Vida Tres, y MásVida. El paciente solo paga la diferencia según su plan. "
    "Para otras ISAPRE (Esencial, Cruz del Norte, etc.), la atención es como particular y "
    "el paciente solicita reembolso directamente a su ISAPRE con la boleta emitida por MediSalud."
)

pdf.subsection("4.3 Seguros complementarios")
pdf.body_text(
    "Aceptamos vouchers y órdenes de los siguientes seguros complementarios: Metlife, Zurich, "
    "Liberty, y BCI Seguros. Otros seguros pueden tramitarse como reembolso posterior. "
    "Para accidentes laborales (Ley 16.744), trabajamos con todas las mutualidades: ACHS, "
    "IST y Mutual de Seguridad. En estos casos, el empleador o la mutualidad cubre el 100% del costo."
)

pdf.subsection("4.4 Atención particular (sin convenio)")
pdf.body_text(
    "Los pacientes sin convenio o que prefieren atención particular abonan el valor completo "
    "al momento de la atención. Los aranceles actuales son: medicina general $35.000 CLP, "
    "especialidades desde $55.000 CLP hasta $90.000 CLP según la especialidad, "
    "urgencias $45.000 CLP más insumos utilizados. Emitimos boleta electrónica para trámites "
    "de reembolso con su seguro."
)

pdf.subsection("4.5 Exámenes de laboratorio e imágenes")
pdf.body_text(
    "Nuestro laboratorio clínico y unidad de imágenes (ecografías, rayos X, scanner) tienen "
    "aranceles propios. Con FONASA: bonificación según arancel MAI. Con ISAPRE convenio: "
    "cobertura según plan individual. Los resultados de laboratorio están disponibles en el "
    "portal del paciente en 24-48 horas hábiles para exámenes de rutina; exámenes especiales "
    "pueden tomar 3-5 días hábiles. Se notifica al paciente por correo cuando están listos."
)

# ─── SECCIÓN 5: INSTRUCCIONES PRE Y POST CONSULTA ────────────────────────────
pdf.add_page()
pdf.section_title("5. Instrucciones Pre y Post Consulta")

pdf.subsection("5.1 Instrucciones generales pre-consulta")
pdf.body_text(
    "Antes de cualquier consulta médica: no consuma alcohol 24 horas antes, informe a su médico "
    "sobre todos los medicamentos que toma (incluyendo suplementos y remedios naturales), "
    "anote sus síntomas, cuándo comenzaron y qué los agrava o alivia, y lleve sus últimos "
    "exámenes de sangre si tiene menos de 6 meses de antigüedad."
)

pdf.subsection("5.2 Exámenes de sangre en ayunas")
pdf.body_text(
    "Para exámenes de sangre que requieren ayuno: ayuno de 8 a 12 horas (solo agua permitida). "
    "No fumar durante el ayuno. Los exámenes de ayuno se realizan de lunes a sábado de 7:30 a 10:00. "
    "Para pacientes diabéticos o con condiciones especiales, consultar con su médico si puede "
    "tomar sus medicamentos habituales durante el ayuno."
)

pdf.subsection("5.3 Ecografías abdominales")
pdf.body_text(
    "Para ecografía abdominal: ayuno de 6 horas mínimo, no consumir gas (bebidas carbonatadas, "
    "legumbres) el día anterior. Para ecografía pélvica: vejiga llena (beber 1 litro de agua "
    "una hora antes y no orinar). Para ecografía de cuello tiroideo o mamas: no se requiere "
    "preparación especial."
)

pdf.subsection("5.4 Colonoscopía y endoscopía")
pdf.body_text(
    "Colonoscopía: el médico indicará la preparación intestinal específica (laxantes el día "
    "anterior). Dieta líquida 24-48 horas antes. Se requiere un acompañante para el traslado "
    "al final del procedimiento (se administra sedación). No conducir el día del procedimiento. "
    "Endoscopía alta: ayuno de 8 horas. Se administra anestesia local en garganta."
)

pdf.subsection("5.5 Instrucciones post-consulta")
pdf.body_text(
    "Después de su consulta: siga las indicaciones de su médico al pie de la letra, "
    "complete el tratamiento completo aunque se sienta mejor antes, consulte si tiene dudas "
    "sobre su receta antes de retirarse. Si el médico solicitó exámenes de seguimiento, "
    "agéndelos antes de salir de la clínica para no perder el turno con especialista."
)

pdf.subsection("5.6 Señales de alarma — cuándo volver de urgencia")
pdf.body_text(
    "Consulte urgencias inmediatamente si presenta: fiebre superior a 39°C, dificultad para "
    "respirar, dolor en el pecho, pérdida de conciencia o confusión, sangrado que no cede, "
    "reacción alérgica severa (hinchazón de cara, garganta, urticaria generalizada). "
    "Para estas situaciones, no espere turno: diríjase directamente a nuestra Unidad de "
    "Urgencias, abierta las 24 horas. En peligro inmediato de vida, llame al 131 (SAMU)."
)

pdf.subsection("5.7 Recetas y medicamentos")
pdf.body_text(
    "Las recetas emitidas en MediSalud tienen validez de 60 días desde la fecha de emisión "
    "(30 días para medicamentos controlados). Si requiere renovar una receta crónica sin nueva "
    "consulta, puede solicitarlo por el portal web hasta por una vez sin cita; a partir de la "
    "segunda renovación consecutiva se requiere control médico. Las farmacias de la clínica "
    "están ubicadas en el primer piso y ofrecen descuento del 10% en medicamentos prescritos "
    "por médicos de MediSalud el mismo día de la consulta."
)

pdf.output("/home/mauricio/RAGAgent/data/clinica_salud.pdf")
print("PDF generado exitosamente.")
