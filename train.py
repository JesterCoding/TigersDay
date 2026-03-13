import argparse
import os
import torch
from ai.trainer import Trainer
from ai.model import save_checkpoint, load_checkpoint
from ai.curriculum import CurriculumManager


def main():
    parser = argparse.ArgumentParser(description="Train AlphaZero AI for The Tiger's Day")
    parser.add_argument('--iterations', type=int, default=100,
                        help="Number of training iterations")
    parser.add_argument('--games', type=int, default=50,
                        help="Self-play games per iteration")
    parser.add_argument('--simulations', type=int, default=100,
                        help="MCTS simulations per move")
    parser.add_argument('--batch-size', type=int, default=256,
                        help="Training batch size")
    parser.add_argument('--lr', type=float, default=1e-3,
                        help="Learning rate")
    parser.add_argument('--resume', type=str, default=None,
                        help="Path to checkpoint to resume from")
    parser.add_argument('--curriculum', action='store_true',
                        help="Enable curriculum learning (start from endgame, work backwards)")
    parser.add_argument('--start-stage', type=int, default=4,
                        help="Curriculum stage to start at (4=endgame, 1=full game)")
    parser.add_argument('--grad-window', type=int, default=200,
                        help="Sliding window size for graduation metrics")
    args = parser.parse_args()

    config = {
        'lr': args.lr,
        'l2_reg': 1e-4,
        'buffer_size': 50000,
        'num_simulations': args.simulations,
        'batch_size': args.batch_size,
        'num_games_per_iteration': args.games,
        'num_training_steps': 100,
        'num_iterations': args.iterations,
        'temperature_threshold': 15,
        'checkpoint_dir': 'ai/checkpoints/',
    }

    # Ensure checkpoint directory exists
    os.makedirs(config['checkpoint_dir'], exist_ok=True)

    # Set up curriculum if enabled
    curriculum = None
    if args.curriculum:
        curriculum = CurriculumManager(
            start_stage=args.start_stage,
            window_size=args.grad_window
        )
        print(f"Curriculum learning enabled, starting at stage {args.start_stage}")

    trainer = Trainer(config, curriculum=curriculum)

    start_iter = 0
    if args.resume:
        start_iter = load_checkpoint(trainer.model, trainer.optimizer, args.resume)
        # Restore curriculum stage from checkpoint
        if curriculum:
            checkpoint = torch.load(args.resume, weights_only=False)
            saved_stage = checkpoint.get('curriculum_stage', None)
            if saved_stage is not None:
                curriculum.current_stage = saved_stage
                print(f"Resumed curriculum at stage {saved_stage}")
        print(f"Resumed from iteration {start_iter}")

    for i in range(start_iter, config['num_iterations']):
        trainer.run_iteration(i)

        # Save best model every 10 iterations
        if (i + 1) % 10 == 0:
            path = f"{config['checkpoint_dir']}best_model.pth"
            # Save with curriculum stage included
            checkpoint_data = {
                'model_state_dict': trainer.model.state_dict(),
                'optimizer_state_dict': trainer.optimizer.state_dict(),
                'iteration': i,
            }
            if curriculum:
                checkpoint_data['curriculum_stage'] = curriculum.current_stage
            torch.save(checkpoint_data, path)
            print(f"Saved best model at iteration {i + 1}")

    print("Training complete.")


if __name__ == "__main__":
    main()
