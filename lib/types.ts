export type Profile={id:string;username:string;display_name:string;avatar_color:string;team_role?:'builder'|'farmer';is_admin?:boolean;created_at?:string};
export type Item={id:string;name_de:string;name_en:string;required:number;stack_size:number;ingredient_name:string|null;ingredient_per_craft:number|null;output_per_craft:number|null;farm_id:string|null;source_hint:string|null;created_at?:string};
export type Farm={id:string;name:string;description:string|null;materials:string|null;schematic_url:string|null;status:string;created_at?:string};
export type Assignment={id:string;target_type:'item'|'farm';target_id:string;user_id:string;created_at?:string};
export type Contribution={id:string;item_id:string;user_id:string;amount:number;created_at:string};
export type FarmMaterial={name:string;quantity:number};
