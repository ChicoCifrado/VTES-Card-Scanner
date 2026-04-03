#!/usr/bin/env python3
"""
Fusionar card_relations_attached.json con card_relations.json
Mapeo inteligente de nombres de archivo
"""
import json
import os
import re

def main():
    print("🔍 Fusionando card_relations.json + card_relations_attached.json...")
    print()
    
    # Rutas
    base_dir = '/home/cifrado/.openclaw/workspace/projects/VTES-Card-Scanner'
    main_relations_path = f'{base_dir}/card_relations.json'
    attached_relations_path = f'{base_dir}/card_relations_attached.json'
    vtes_path = f'{base_dir}/vtes.json'
    output_path = f'{base_dir}/card_relations_fused.json'
    
    # Cargar datos
    with open(main_relations_path, 'r', encoding='utf-8') as f:
        main_relations = json.load(f)
    with open(attached_relations_path, 'r', encoding='utf-8') as f:
        attached_relations = json.load(f)
    with open(vtes_path, 'r', encoding='utf-8') as f:
        vtes_cards = json.load(f)
    
    print(f"✅ Cargados correctamente")
    print(f"   Total cartas en card_relations.json: {main_relations['total_cards']}")
    print(f"   Total imágenes con attached: {len(attached_relations['relations_by_image'])}")
    print()
    
    # Crear mapeo: nombre_sin_extensión -> lista de cartas
    # vtes.json tiene cards con 'name' y '_name'
    file_to_cards = {}
    for card in vtes_cards:
        card_name = card.get('name', card.get('_name', ''))
        card_url = card.get('url', '')
        # Extraer nombre de archivo desde URL (sin extensión)
        if card_url:
            # Intentar extraer nombre completo con extensión
            match = re.search(r'/([^/]+)\.(jpg|png)', card_url)
            if match:
                filename_full = match.group(1) + '.' + match.group(2)
                # Nombre sin extensión también
                filename_noext = match.group(1)
                
                if filename_full not in file_to_cards:
                    file_to_cards[filename_full] = []
                file_to_cards[filename_full].append({
                    'id': str(card.get('id', '')),
                    'name': card_name
                })
                
                if filename_noext not in file_to_cards:
                    file_to_cards[filename_noext] = []
                file_to_cards[filename_noext].append({
                    'id': str(card.get('id', '')),
                    'name': card_name
                })
    
    print(f"   Mapeo archivo->carta: {len(file_to_cards)} entradas")
    print()
    
    # Procesar relaciones attached
    print(f"🔗 Agregando 'attached' a cartas solapadas...")
    
    for img_data in attached_relations['relations_by_image']:
        attached_pairs = img_data.get('attached_pairs', [])
        
        for pair in attached_pairs:
            card1_filename = pair.get('card1_name', '')
            card2_filename = pair.get('card2_name', '')
            iou = pair.get('iou', 0)
            
            # Intentar mapeo flexible
            card1_matches = file_to_cards.get(card1_filename, file_to_cards.get(card1_filename.split('.')[0], []))
            card2_matches = file_to_cards.get(card2_filename, file_to_cards.get(card2_filename.split('.')[0], []))
            
            # Si hay matches
            if card1_matches and card2_matches:
                # Usar primera coincidencia (por ID)
                card1_data = card1_matches[0]
                card2_data = card2_matches[0]
                
                card1_name = card1_data.get('name', '')
                card2_name = card2_data.get('name', '')
                
                print(f"   Found: {card1_name} + {card2_name} (IoU={iou:.4f})")
                
                # Buscar en main_relations
                for relation_type in ['equipos', 'retainers', 'variants', 'titulos', 'clans_rare']:
                    card_list = main_relations['relations'][relation_type]
                    for card in card_list:
                        card_id = str(card.get('id', ''))
                        
                        # Añadir a carta 1
                        if card_id == card1_data['id']:
                            if 'attached' not in card:
                                card['attached'] = []
                            card['attached'].append({
                                'card2': card2_name,
                                'iou': iou,
                                'source': 'card_relations_attached.json'
                            })
                        
                        # Añadir a carta 2
                        elif card_id == card2_data['id']:
                            if 'attached' not in card:
                                card['attached'] = []
                            card['attached'].append({
                                'card1': card1_name,
                                'iou': iou,
                                'source': 'card_relations_attached.json'
                            })
            else:
                # Carta no encontrada
                pass
    
    print()
    
    # Guardar resultado
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(main_relations, f, indent=2, ensure_ascii=False)
    
    # Estadísticas
    total_attached_cards = 0
    total_attached_relations = 0
    for relation_type in ['equipos', 'retainers', 'variants', 'titulos', 'clans_rare']:
        for card in main_relations['relations'][relation_type]:
            if 'attached' in card:
                total_attached_cards += 1
                total_attached_relations += len(card['attached'])
    
    print(f"📊 Fusión completada:")
    print(f"   - Cartas con 'attached': {total_attached_cards}")
    print(f"   - Total relaciones added: {total_attached_relations}")
    print()
    print(f"📄 Guardado en: {output_path}")
    print()
    print("✅ ¡Completado!")

if __name__ == '__main__':
    main()