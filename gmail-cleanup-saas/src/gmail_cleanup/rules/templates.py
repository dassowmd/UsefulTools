"""Template rules for common email cleanup scenarios."""

from typing import List, Dict, Any
from datetime import datetime
import uuid

from .models import Rule, RuleCriteria, RuleAction, ActionType


class RuleTemplates:
    """Collection of common rule templates."""
    
    @staticmethod
    def get_all_templates() -> List[Dict[str, Any]]:
        """Get all available rule templates."""
        return [
            RuleTemplates.delete_old_emails(),
            RuleTemplates.auto_read_notifications(),
            RuleTemplates.delete_newsletters(),
            RuleTemplates.auto_read_social_media(),
            RuleTemplates.delete_promotional(),
            RuleTemplates.archive_receipts(),
            RuleTemplates.delete_large_attachments(),
            RuleTemplates.auto_read_automated_emails(),
            RuleTemplates.delete_spam_keywords(),
            RuleTemplates.organize_by_domain(),
        ]
    
    @staticmethod
    def delete_old_emails(days: int = 365) -> Dict[str, Any]:
        """Template for deleting old emails."""
        return {
            'id': 'delete_old_emails',
            'name': f'Delete emails older than {days} days',
            'description': f'Automatically delete emails that are older than {days} days to free up storage space',
            'criteria': {
                'older_than_days': days
            },
            'action': {
                'type': 'delete'
            },
            'category': 'storage',
            'risk_level': 'medium'
        }
    
    @staticmethod
    def auto_read_notifications() -> Dict[str, Any]:
        """Template for auto-reading notification emails."""
        return {
            'id': 'auto_read_notifications',
            'name': 'Auto-read notification emails',
            'description': 'Automatically mark notification emails as read',
            'criteria': {
                'from_domain': 'notifications.example.com',
                'is_unread': True
            },
            'action': {
                'type': 'mark_read'
            },
            'category': 'productivity',
            'risk_level': 'low'
        }
    
    @staticmethod
    def delete_newsletters(days: int = 30) -> Dict[str, Any]:
        """Template for deleting newsletter emails."""
        return {
            'id': 'delete_newsletters',
            'name': f'Delete newsletters older than {days} days',
            'description': f'Delete newsletter and marketing emails older than {days} days',
            'criteria': {
                'has_words': 'unsubscribe',
                'older_than_days': days
            },
            'action': {
                'type': 'delete'
            },
            'category': 'marketing',
            'risk_level': 'low'
        }
    
    @staticmethod
    def auto_read_social_media() -> Dict[str, Any]:
        """Template for auto-reading social media notifications."""
        return {
            'id': 'auto_read_social_media',
            'name': 'Auto-read social media notifications',
            'description': 'Automatically mark social media notifications as read',
            'criteria': {
                'has_words': 'notification',
                'from_domain': 'facebook.com'  # Can be customized
            },
            'action': {
                'type': 'mark_read'
            },
            'category': 'social',
            'risk_level': 'low'
        }
    
    @staticmethod
    def delete_promotional(days: int = 7) -> Dict[str, Any]:
        """Template for deleting promotional emails."""
        return {
            'id': 'delete_promotional',
            'name': f'Delete promotional emails older than {days} days',
            'description': f'Delete promotional and sales emails older than {days} days',
            'criteria': {
                'labels': ['CATEGORY_PROMOTIONS'],
                'older_than_days': days
            },
            'action': {
                'type': 'delete'
            },
            'category': 'marketing',
            'risk_level': 'low'
        }
    
    @staticmethod
    def archive_receipts() -> Dict[str, Any]:
        """Template for archiving receipt emails."""
        return {
            'id': 'archive_receipts',
            'name': 'Archive receipt emails',
            'description': 'Archive emails containing receipts and order confirmations',
            'criteria': {
                'has_words': 'receipt OR invoice OR "order confirmation"',
                'older_than_days': 30
            },
            'action': {
                'type': 'add_label',
                'parameters': {
                    'labels': ['receipts']
                }
            },
            'category': 'organization',
            'risk_level': 'medium'
        }
    
    @staticmethod
    def delete_large_attachments(size_mb: int = 25, days: int = 90) -> Dict[str, Any]:
        """Template for deleting emails with large attachments."""
        size_bytes = size_mb * 1024 * 1024
        return {
            'id': 'delete_large_attachments',
            'name': f'Delete emails with attachments larger than {size_mb}MB',
            'description': f'Delete emails with large attachments (>{size_mb}MB) older than {days} days',
            'criteria': {
                'has_attachment': True,
                'size_larger_than': size_bytes,
                'older_than_days': days
            },
            'action': {
                'type': 'delete'
            },
            'category': 'storage',
            'risk_level': 'high'
        }
    
    @staticmethod
    def auto_read_automated_emails() -> Dict[str, Any]:
        """Template for auto-reading automated emails."""
        return {
            'id': 'auto_read_automated',
            'name': 'Auto-read automated emails',
            'description': 'Automatically mark automated system emails as read',
            'criteria': {
                'from_email': 'noreply@',
                'is_unread': True
            },
            'action': {
                'type': 'mark_read'
            },
            'category': 'automation',
            'risk_level': 'low'
        }
    
    @staticmethod
    def delete_spam_keywords(days: int = 1) -> Dict[str, Any]:
        """Template for deleting emails with spam keywords."""
        return {
            'id': 'delete_spam_keywords',
            'name': f'Delete spam emails older than {days} day',
            'description': 'Delete emails containing common spam keywords',
            'criteria': {
                'has_words': 'urgent action required OR limited time offer OR act now',
                'older_than_days': days
            },
            'action': {
                'type': 'delete'
            },
            'category': 'spam',
            'risk_level': 'low'
        }
    
    @staticmethod
    def organize_by_domain() -> Dict[str, Any]:
        """Template for organizing emails by domain."""
        return {
            'id': 'organize_by_domain',
            'name': 'Label emails by sender domain',
            'description': 'Add labels to emails based on sender domain',
            'criteria': {
                'from_domain': 'example.com'  # To be customized
            },
            'action': {
                'type': 'add_label',
                'parameters': {
                    'labels': ['domain/example']
                }
            },
            'category': 'organization',
            'risk_level': 'low'
        }
    
    @staticmethod
    def create_rule_from_template(template_id: str, **customizations) -> Rule:
        """Create a rule from a template with customizations.
        
        Args:
            template_id: ID of the template to use
            **customizations: Custom values to override template defaults
            
        Returns:
            Rule object created from template
        """
        templates = {t['id']: t for t in RuleTemplates.get_all_templates()}
        
        if template_id not in templates:
            raise ValueError(f"Template '{template_id}' not found")
        
        template = templates[template_id].copy()
        
        # Apply customizations
        for key, value in customizations.items():
            if key in ['name', 'description']:
                template[key] = value
            elif key.startswith('criteria_'):
                criteria_key = key[9:]  # Remove 'criteria_' prefix
                template['criteria'][criteria_key] = value
            elif key.startswith('action_'):
                action_key = key[7:]  # Remove 'action_' prefix
                if action_key == 'type':
                    template['action']['type'] = value
                else:
                    if 'parameters' not in template['action']:
                        template['action']['parameters'] = {}
                    template['action']['parameters'][action_key] = value
        
        # Create rule object
        return Rule(
            id=str(uuid.uuid4()),
            name=template['name'],
            description=template['description'],
            criteria=RuleCriteria.from_dict(template['criteria']),
            action=RuleAction.from_dict(template['action']),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @staticmethod
    def get_template_by_category(category: str) -> List[Dict[str, Any]]:
        """Get templates by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of templates in the category
        """
        all_templates = RuleTemplates.get_all_templates()
        return [t for t in all_templates if t.get('category') == category]
    
    @staticmethod
    def get_categories() -> List[str]:
        """Get all available categories.
        
        Returns:
            List of unique categories
        """
        all_templates = RuleTemplates.get_all_templates()
        categories = set()
        for template in all_templates:
            if 'category' in template:
                categories.add(template['category'])
        return sorted(list(categories))
    
    @staticmethod
    def customize_domain_template(template_id: str, domain: str) -> Dict[str, Any]:
        """Customize a template for a specific domain.
        
        Args:
            template_id: ID of the template to customize
            domain: Domain to customize for
            
        Returns:
            Customized template dict
        """
        templates = {t['id']: t for t in RuleTemplates.get_all_templates()}
        
        if template_id not in templates:
            raise ValueError(f"Template '{template_id}' not found")
        
        template = templates[template_id].copy()
        
        # Update name and description
        template['name'] = template['name'].replace('example.com', domain)
        template['description'] = template['description'].replace('example.com', domain)
        
        # Update criteria
        if 'from_domain' in template['criteria']:
            template['criteria']['from_domain'] = domain
        
        # Update action parameters if needed
        if (template['action']['type'] in ['add_label', 'remove_label'] and
            'parameters' in template['action'] and
            'labels' in template['action']['parameters']):
            
            labels = template['action']['parameters']['labels']
            updated_labels = []
            for label in labels:
                if 'example' in label:
                    updated_labels.append(label.replace('example', domain.split('.')[0]))
                else:
                    updated_labels.append(label)
            template['action']['parameters']['labels'] = updated_labels
        
        return template