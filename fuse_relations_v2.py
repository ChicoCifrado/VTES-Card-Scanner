#!/usr/bin/env python3
"""
Fusionar card_relations_attached.json con card_relations.json
Mapear nombres de archivo a nombres de cartas usando vtes.json
"""
import json
import os

def main():
    print("🔍 Fusionando card_relations.json + card_relations_attached.json...")
    print()
    
    # Rutas
    base_dir = '/home/cifrado/.openclaw/workspace/projects/VTES-Card-Scanner'
    main_relations_path = f'{base_dir}/card_relations.json'
    attached_relations_path = f'{base_dir}/card_relations_attached.json'
    vtes_path = f'{base_dir}/vtes.json'
    output_path = f'{base_dir}/card_relations_fused.json'
    
    # Cargar card_relations.json principal
    with open(main_relations_path, 'r', encoding='utf-8') as f:
        main_relations = json.load(f)
    
    # Cargar card_relations_attached.json
    with open(attached_relations_path, 'r', encoding='utf-8') as f:
        attached_relations = json.load(f)
    
    # Cargar vtes.json para mapear nombres de archivo
    with open(vtes_path, 'r', encoding='utf-8') as f:
        vtes_cards = json.load(f)
    
    print(f"✅ Cargados correctamente")
    print(f"   Total cartas en card_relations.json: {main_relations['total_cards']}")
    print(f"   Total imágenes con attached: {len(attached_relations['relations_by_image'])}")
    print()
    
    # Crear diccionario de mapeo: nombre_archivo -> card
    # vtes.json tiene cards con 'name' y 'url' o '_name'
    file_to_card = {}
    for card in vtes_cards:
        card_name = card.get('name', card.get('_name', ''))
        card_url = card.get('url', '')
        # Extraer nombre de archivo desde URL
        if card_url:
            import re
            match = re.search(r'/([^/]+)\.jpg', card_url)
            if match:
                filename = match.group(1)
                file_to_card[filename] = {
                    'id': card.get('id', ''),
                    'name': card_name,
                    'url': card_url
                }
    
    print(f"   Mapeo archivo->carta: {len(file_to_card)} cartas")
    print()
    
    # Procesar relaciones attached
    print(f"🔗 Agregando 'attached' a cartas solapadas...")
    
    for img_data in attached_relations['relations_by_image']:
        attached_pairs = img_data.get('attached_pairs', [])
        
        for pair in attached_pairs:
            card1_filename = pair.get('card1_name', '')
            card2_filename = pair.get('card2_name', '')
            iou = pair.get('iou', 0)
            
            # Mapear a cartas reales
            card1_data = file_to_card.get(card1_filename, {})
            card2_data = file_to_card.get(card2_filename, {})
            
            # Si ambas cartas existen en vtes, añadir attached
            if card1_data and card2_data:
                card1_name = card1_data.get('name', '')
                card2_name = card2_data.get('name', '')
                card1_id = card1_data.get('id', '')
                card2_id = card2_data.get('id', '')
                
                print(f"   Found: {card1_name} + {card2_name} (IoU={iou:.4f})")
                
                # Buscar estas cartas en los diferentes tipos de relaciones
                for relation_type in ['equipos', 'retainers', 'variants', 'titulos', 'clans_rare']:
                    for card_list in [main_relations['relations'][relation_type]]:
                        for card in card_list:
                            # Buscar por ID
                            if str(card.get('id', '')) == card1_id:
                                if 'attached' not in card:
                                    card['attached'] = []
                                card['attached'].append({
                                    'card2': card2_name,
                                    'card2_id': card2_id,
                                    'iou': iou,
                                    'source': 'card_relations_attached.json',
                                    'original_filename': card1_filename
                                })
                            elif str(card.get('id', '')) == card2_id:
                                if 'attached' not in card:
                                    card['attached'] = []
                                card['attached'].append({
                                    'card1': card1_name,
                                    'card1_id': card1_id,
                                    'iou': iou,
                                    'source': 'card_relations_attached.json',
                                    'original_filename': card2_filename
                                })
            else:
                # Carta no encontrada, mantener sin attached
                pass
    
    print()
    
    # Guardar resultado
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(main_relations, f, indent=2, ensure_ascii=False)
    
    # Estadísticas
    total_attached_cards = 0
    for relation_type in ['equipos', 'retainers', 'variants', 'titulos', 'clans_rare']:
        for card in main_relations['relations'][relation_type]:
            if 'attached' in card:
                total_attached_cards += 1
    
    print(f"📊 Fusión completada:")
    print(f"   - Cartas con 'attached': {total_attached_cards}")
    print(f"   - Total relaciones added: ", end='')
    
    total_attached_relations = sum(
        img_data.get('num_attached_pairs', 0)
        for img_data in attached_relations['relations_by_image']
    )
    print(total_attached_relations)
    print()
    print(f"📄 Guardado en: {output_path}")
    print()
    print("✅ ¡Completado!")

if __name__ == '__main__':
    main()