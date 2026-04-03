#!/usr/bin/env python3
"""
Fusionar card_relations_attached.json con card_relations.json
Añadir campo 'attached' a cartas solapadas
"""
import json

def main():
    print("🔍 Fusionando card_relations.json + card_relations_attached.json...")
    print()
    
    # Rutas
    base_dir = '/home/cifrado/.openclaw/workspace/projects/VTES-Card-Scanner'
    main_relations_path = f'{base_dir}/card_relations.json'
    attached_relations_path = f'{base_dir}/card_relations_attached.json'
    output_path = f'{base_dir}/card_relations_fused.json'
    
    # Cargar card_relations.json principal
    with open(main_relations_path, 'r', encoding='utf-8') as f:
        main_relations = json.load(f)
    
    # Cargar card_relations_attached.json
    with open(attached_relations_path, 'r', encoding='utf-8') as f:
        attached_relations = json.load(f)
    
    print(f"✅ Cargados correctamente")
    print(f"   Total cartas: {main_relations['total_cards']}")
    print(f"   Total imágenes con attached: {len(attached_relations['relations_by_image'])}")
    print()
    
    # Extraer todas las cartas del JSON principal
    all_card_names = {}
    for relation_type in ['equipos', 'retainers', 'variants', 'titulos', 'clans_rare']:
        for card in main_relations['relations'][relation_type]:
            card_id = card.get('id', 0)
            # Usar 'name' si existe (retainers, clans_rare), 'original'/'variant' si es variants, 'name' en otros
            if relation_type == 'variants':
                # En variants, usar card1_name o card2_name
                card_name = card.get('original', {}).get('name', card.get('variant', {}).get('name', 'unknown'))
            else:
                card_name = card.get('name', card.get('_name', 'unknown'))
            all_card_names[card_name] = {
                'id': card_id,
                'relation_type': relation_type,
                'name': card_name
            }
    
    print(f"   Total cartas indexadas: {len(all_card_names)}")
    print()
    
    # Procesar relaciones attached
    print(f"🔗 Agregando 'attached' a cartas solapadas...")
    
    for img_data in attached_relations['relations_by_image']:
        attached_pairs = img_data.get('attached_pairs', [])
        
        for pair in attached_pairs:
            card1_name = pair.get('card1_name', '')
            card2_name = pair.get('card2_name', '')
            iou = pair.get('iou', 0)
            
            # Añadir field 'attached' a ambas cartas si existen
            if card1_name in all_card_names:
                all_card_names[card1_name]['attached'] = all_card_names[card1_name].get('attached', [])
                all_card_names[card1_name]['attached'].append({
                    'card2': card2_name,
                    'iou': iou,
                    'source': 'card_relations_attached.json'
                })
            
            if card2_name in all_card_names:
                all_card_names[card2_name]['attached'] = all_card_names[card2_name].get('attached', [])
                all_card_names[card2_name]['attached'].append({
                    'card1': card1_name,
                    'iou': iou,
                    'source': 'card_relations_attached.json'
                })
    
    # Actualizar el JSON principal
    total_attached_cards = 0
    for relation_type in ['equipos', 'retainers', 'variants', 'titulos', 'clans_rare']:
        for card in main_relations['relations'][relation_type]:
            # Usar .get con fallback
            card_name = card.get('name', card.get('_name', card.get('printed_name', '')))
            if card_name in all_card_names:
                if 'attached' in all_card_names[card_name]:
                    total_attached_cards += 1
                    # Actualizar carta
                    if 'attached' not in card:
                        card['attached'] = []
                    card['attached'].extend(all_card_names[card_name]['attached'])
    
    print()
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